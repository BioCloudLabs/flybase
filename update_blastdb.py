from json import load
from subprocess import run
from docker import from_env
from os import getcwd
from multiprocessing import Pool


container = from_env().containers.run(
    'ncbi/blast',
    'tail -f /dev/null',
    detach=True,
    volumes=[
        f'{getcwd()}/fasta:/blast/fasta:ro',
        f'{getcwd()}/blastdb_custom:/blast/blastdb_custom:rw'
    ],
    auto_remove=True,
    working_dir='/blast/blastdb_custom'
)


def func(args):
    drosophila, fasta = args

    run(['curl', '-o', f'{getcwd()}/fasta/{fasta}.gz', f'https://ftp.flybase.net/genomes/{drosophila}/current/fasta/{fasta}.gz'])

    run(['gunzip', f'{getcwd()}/fasta/{fasta}.gz'])

    container.exec_run(f"makeblastdb -in /blast/fasta/{fasta} -dbtype nucl -parse_seqids -out {fasta.replace('.fasta', '')} -blastdb_version 5")

    run(['rm', f'{getcwd()}/fasta/{fasta}'])


with open('genomes.json', 'r') as genomes:
    with Pool() as pool:
        pool.map(func, [(drosophila, fasta) for drosophila, current in load(genomes).items() for fasta in current])
