from json import load  # Importing the load function to read JSON data
from subprocess import run  # Importing run to execute shell commands
from docker import from_env  # Importing from_env to interact with the Docker environment
from os import getcwd  # Importing getcwd to get the current working directory
from multiprocessing import Pool  # Importing Pool to parallelize tasks

# Start a Docker container running the 'ncbi/blast' image, with an idle command to keep it running
container = from_env().containers.run(
    'ncbi/blast',  # Docker image to use
    'tail -f /dev/null',  # Command to keep the container running
    detach=True,  # Run the container in detached mode
    volumes=[
        f'{getcwd()}/fasta:/blast/fasta:ro',  # Mount the 'fasta' directory as read-only
        f'{getcwd()}/blastdb_custom:/blast/blastdb_custom:rw'  # Mount the 'blastdb_custom' directory with read-write permissions
    ],
    auto_remove=True,  # Automatically remove the container when it exits
    working_dir='/blast/blastdb_custom'  # Set the working directory inside the container
)

# Function to process each genome and FASTA file
def func(args):
    drosophila, fasta = args

    # Download the FASTA file using curl
    run(['curl', '-o', f'{getcwd()}/fasta/{fasta}.gz', f'https://ftp.flybase.net/genomes/{drosophila}/current/fasta/{fasta}.gz'])

    # Decompress the downloaded FASTA file
    run(['gunzip', f'{getcwd()}/fasta/{fasta}.gz'])

    # Run the makeblastdb command inside the Docker container to create a BLAST database
    container.exec_run(f"makeblastdb -in /blast/fasta/{fasta} -dbtype nucl -parse_seqids -out {fasta.replace('.fasta', '')} -blastdb_version 5")

    # Remove the decompressed FASTA file to clean up
    run(['rm', f'{getcwd()}/fasta/{fasta}'])

# Read the genomes JSON file
with open('genomes.json', 'r') as genomes:
    # Create a multiprocessing pool to parallelize the task
    with Pool() as pool:
        # Map the func function to each drosophila and fasta pair from the JSON data
        pool.map(func, [(drosophila, fasta) for drosophila, current in load(genomes).items() for fasta in current])
