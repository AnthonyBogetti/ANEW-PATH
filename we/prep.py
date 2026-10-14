import os
import shutil
import numpy as np
import subprocess
import logging
import re
import sys


    def step4_setup_westpa(self):
        try:
            from prody import parsePDB, calcAdaptiveANM, writeDCD, AANM_ALTERNATING, LOGGER
        except ImportError:
            raise ImportError("Please install 'prody' (conda install -c conda-forge prody) to use this module.")

        md_dir = self.md_dir
        print(f"Sourcing MD files from: {md_dir}")

        we_setups = [
            ("a2b", "closed", "open"),
            ("b2a", "open", "closed")
        ]

        for we_folder, start_state, target_state in we_setups:
            folder_path = os.path.join(self.output_dir, we_folder)
            
            if os.path.exists(folder_path):
                shutil.rmtree(folder_path)
            
            shutil.copytree(self.we_template, folder_path)

            slurm_path = os.path.join(folder_path, "runwe.slurm")
            if os.path.exists(slurm_path):
                with open(slurm_path, "r") as f:
                    slurm_code = f.read()
                slurm_code = slurm_code.replace("#SBATCH --job-name=a2b", f"#SBATCH --job-name={we_folder}")
                with open(slurm_path, "w") as f:
                    f.write(slurm_code)
                print(f"  -> [{we_folder}] Updated job name in runwe.slurm.")

            common_files = os.path.join(folder_path, "common_files")
            bstates = os.path.join(folder_path, "bstates")

            if os.path.exists(md_dir):
                shutil.copy(os.path.join(md_dir, f"{start_state}.prmtop"), os.path.join(common_files, "top.prmtop"))
                shutil.copy(os.path.join(md_dir, f"{target_state}.prmtop"), os.path.join(common_files, "b.prmtop"))

                start_rst7 = os.path.join(md_dir, f"{start_state}_eq_free.rst7")
                target_rst7 = os.path.join(md_dir, f"{target_state}_eq_free.rst7")
                out_start_ncrst = os.path.join(bstates, "bstate.ncrst")
                out_target_ncrst = os.path.join(common_files, "b.ncrst")

                # --- UPDATED CPPTRAJ AUTOMATION ---
                # This explicitly unwraps the disjointed segments, centers them as a single 
                # collective mass, and images the solvent around them.
                solute_mask = "!(:WAT,HOH,Na+,Cl-,K+,Mg2+)"
                
                for rst_in, prm, rst_out in [(start_rst7, os.path.join(md_dir, f"{start_state}.prmtop"), out_start_ncrst),
                                             (target_rst7, os.path.join(md_dir, f"{target_state}.prmtop"), out_target_ncrst)]:
                    cpptraj_cmd = f"""parm {prm}
trajin {rst_in}
unwrap {solute_mask}
center {solute_mask} mass origin
image origin center familiar
trajout {rst_out}
run
"""
                    subprocess.run(["cpptraj"], input=cpptraj_cmd, text=True, check=True)

                a_pdb = os.path.join(common_files, "a.pdb")
                b_pdb = os.path.join(common_files, "b.pdb")
                a_ca_pdb = os.path.join(common_files, "a_ca.pdb")
                b_ca_pdb = os.path.join(common_files, "b_ca.pdb")

                if start_state == "closed":
                    subprocess.run(f"ambpdb -c {out_start_ncrst} -p {os.path.join(common_files, 'top.prmtop')} > {a_pdb}", shell=True)
                    subprocess.run(f"ambpdb -c {out_target_ncrst} -p {os.path.join(common_files, 'b.prmtop')} > {b_pdb}", shell=True)
                else:
                    subprocess.run(f"ambpdb -c {out_target_ncrst} -p {os.path.join(common_files, 'b.prmtop')} > {a_pdb}", shell=True)
                    subprocess.run(f"ambpdb -c {out_start_ncrst} -p {os.path.join(common_files, 'top.prmtop')} > {b_pdb}", shell=True)

                subprocess.run(f'cat {a_pdb} | grep " CA " > {a_ca_pdb}', shell=True)
                subprocess.run(f'cat {b_pdb} | grep " CA " > {b_ca_pdb}', shell=True)

                start_pdb_source = a_pdb if start_state == "closed" else b_pdb
                start_ca_source = a_ca_pdb if start_state == "closed" else b_ca_pdb
                shutil.copy(start_pdb_source, os.path.join(bstates, "bstate.pdb"))
                shutil.copy(start_ca_source, os.path.join(bstates, "bstate_ca.pdb"))

            original_pwd = os.getcwd()
            os.chdir(common_files)
            try:
                if we_folder == "a2b":
                    print(f"  -> [{we_folder}] Calculating Adaptive ANM and validating convergence...")
                    catcher = RMSDCatcher()
                    LOGGER._logger.addHandler(catcher) 

                    try:
                        a = parsePDB("a.pdb", subset="ca")
                        b = parsePDB("b.pdb", subset="ca")
                        ens = calcAdaptiveANM(a, b, 20, mode=AANM_ALTERNATING)
                        
                        if not catcher.rmsds:
                            raise ValueError("ProDy aANM did not report any RMSD values.")
                        
                        final_rmsd = catcher.rmsds[-1]
                        print(f"  -> [{we_folder}] Final convergence RMSD: {final_rmsd:.2f} Å")
                        
                        if final_rmsd > 5.0:
                            raise ValueError(f"CRITICAL: aANM failed to converge below 5Å (Final: {final_rmsd:.2f}Å). Aborting.")
                        
                        writeDCD("ens.dcd", ens)
                    finally:
                        LOGGER._logger.removeHandler(catcher)
                
                elif we_folder == "b2a":
                    print(f"  -> [{we_folder}] Copying ens.dcd from a2b...")
                    a2b_dcd_path = os.path.join(self.output_dir, "a2b", "common_files", "ens.dcd")
                    if os.path.exists(a2b_dcd_path):
                        shutil.copy(a2b_dcd_path, "ens.dcd")
                    
                    score_py_path = "score.py"
                    if os.path.exists(score_py_path):
                        with open(score_py_path, "r") as f:
                            score_code = f.read()
                        score_code = score_code.replace('midpts = np.load("midpoints.npy")', 'midpts = np.load("midpoints.npy")[::-1]')
                        with open(score_py_path, "w") as f:
                            f.write(score_code)
                        print(f"  -> [{we_folder}] Updated score.py with reverse slicing.")
            finally:
                os.chdir(original_pwd)

            # Analysis and Shell scripts generation (find_pcoord.py and post_iter.sh)
            analysis_dir = os.path.join(folder_path, "analysis")
            os.makedirs(analysis_dir, exist_ok=True)
            target_rmsd = "rmsd2b" if we_folder == "a2b" else "rmsd2a"
            
            with open(os.path.join(analysis_dir, "find_pcoord.py"), "w") as f:
                f.write(f"""import h5py
import sys
f = h5py.File("../west.h5", "r")
n_iters = f['summary'][:].shape[0]
target_reached = False
for i in range(1, n_iters):
    aux_str = f"iterations/iter_{{str(i).zfill(8)}}/auxdata/{target_rmsd}"
    if aux_str in f:
        aux = f[aux_str][:,-1]
        for idx, val in enumerate(aux):
            if val < 3:
                target_reached = True
                break
    if target_reached: break
if target_reached:
    with open("../TARGET_REACHED", "w") as out: out.write("DONE\\n")
""")
            
            westpa_scripts_dir = os.path.join(folder_path, "westpa_scripts")
            os.makedirs(westpa_scripts_dir, exist_ok=True)
            with open(os.path.join(westpa_scripts_dir, "post_iter.sh"), "w") as f:
                f.write("""#!/bin/bash
cd $WEST_SIM_ROOT || exit 1
ITER=$(printf "%06d" $WEST_CURRENT_ITER)
tar -cf seg_logs/$ITER.tar seg_logs/$ITER-*.log
rm -f seg_logs/$ITER-*.log
rm -rf traj_segs/$ITER
rm -rf $WEST_SIM_ROOT/tmp/*
if (( WEST_CURRENT_ITER % 10 == 0 )); then
    cd $WEST_SIM_ROOT/analysis && python find_pcoord.py && cd $WEST_SIM_ROOT
    if [ -f "TARGET_REACHED" ]; then
        sed -i -e "s/max_total_iterations:.*/max_total_iterations: $WEST_CURRENT_ITER/g" west.cfg
    fi
fi
""")
            os.chmod(os.path.join(westpa_scripts_dir, "post_iter.sh"), 0o755)
            self._write_to_shell(f"echo \"--- Initializing WESTPA for {we_folder} ---\"")
            self._write_to_shell(f"cd {folder_path} && ./init.sh && sbatch runwe.slurm && cd ..")

