import argparse
import os, subprocess
from pdb import run
import torch

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    
    n_gpus = torch.cuda.device_count()
    print(n_gpus)
    if os.getenv("SM_NUM_GPUS") == None:
        print("Explicitly specifying the number of GPUs.")
        os.environ["GPU_NUM_DEVICES"] = str(n_gpus)
    else:
        os.environ["GPU_NUM_DEVICES"] = os.environ["SM_NUM_GPUS"]
        
    # hyperparameters sent by the client are passed as command-line arguments to the script.
    parser.add_argument("--training_script", type=str, default="train.py")
    parser.add_argument("--n_gpus", type=str, default=os.environ["GPU_NUM_DEVICES"])
    #parser.add_argument("--output_dir", type=str, default=os.environ["SM_OUTPUT_DIR"])
    parser.add_argument("--output_dir", type=str, default='./output')
    
    args, rem_args = parser.parse_known_args()
    print("Parsed Arguments: ", vars(args), rem_args)

    # native torch distributed as benchmark
    training_command = "python -m torch.distributed.launch "
    training_command += f"--nproc_per_node={args.n_gpus} "
    training_command += "--nnodes=1 --node_rank=0 --master_addr=127.0.0.1 --master_port=1234 "

    training_command += args.training_script + " "

    # output directory
    training_command += f"--output_dir {args.output_dir} "
    for i in range(0, len(rem_args), 2):
        arg, value = rem_args[i], rem_args[i + 1]
        if value == "True":
            training_command += f"{arg} "
        elif value != "False":
            training_command += f"{arg} {value} "

    print("Training Command: ", training_command)
    #subprocess.check_call(training_command, shell=True)
