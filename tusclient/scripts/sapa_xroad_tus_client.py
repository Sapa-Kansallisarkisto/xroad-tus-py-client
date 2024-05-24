"""A script to send files with TUS via an X-Road server connection to SAPA

The client key and certificate must be created and added to the X-Road server
for authentication. Create with:

 openssl genrsa -out clientprivatekey.pem 4096
 openssl req -new -x509 -key clientprivatekey.pem -out clientcert.pem -days 365

The certificate must be added in the X-Road UI (usually on port 4000) at
 Clients
 -> [subsystem]
 -> Internal servers
 -> Information System TLS certificate
 -> [+ Add]

SAPA:
  You require the following information before you can upload:
    package_type
    ahaa_series_id
    transfer_oid
    digitization_rationale, IF package is a digitization package

"""
import sys
import click
import os
import hashlib
from tusclient import client


def md5_file(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


@click.command()
@click.option('--target_url', type=str,
              default='https://xroad-test.xroad.test/r1/' +
                      'XX-TEST/GOV/1234567-8/testservice/ws/' +
                      'api/latest/tus_upload',
              help='The target URL endpoint / X-Road server path')
@click.option('--xroad_client', type=str,
              default='XX-TEST/GOV/8765432-1/testclient',
              help='The X-Road client path to use')
@click.option('--xroad_client_key', type=click.Path(exists=False),
              default='./clientprivatekey.pem.test',
              help='The client key to use')
@click.option('--xroad_client_cert', type=click.Path(exists=False),
              default='./clientcert.pem.test',
              help='The client certificate to use')
@click.option('--verify', type=bool, is_flag=True, default=False,
              help='Verify client certificate')
@click.option('--api_key', type=str, default=None,
              help='API Key')
@click.option('--file', type=str, default="",
              help='File to upload via TUS')
@click.option('--package_checksum', type=bool, is_flag=True, default=True,
              help='SAPA - Add checksum for package, default is True')
@click.option('--package_type', type=str, default=None,
              help='SAPA - Package type')
@click.option('--ahaa_series_id', type=str, default=None,
              help='SAPA - AHAA metadata series ID')
@click.option('--transfer_oid', type=str, default=None,
              help='SAPA - ID for the transfer')
@click.option('--email_notify_to', type=str, default=None,
              help='SAPA - Optional email for notifications')
@click.option('--digitization_rationale', type=str, default=None,
              help='SAPA - Optional but mandatory UUID for ' +
              'digitization packages')
def main(target_url,
         xroad_client,
         xroad_client_key,
         xroad_client_cert,
         verify,
         api_key,
         file,
         package_checksum,
         package_type,
         ahaa_series_id,
         transfer_oid,
         email_notify_to,
         digitization_rationale):
    """Will execute a TUS upload through the X-Road server
    :param target_url: Target X-Road server URL
    :param xroad_client: X-Road client path string
    :param xroad_client_key: Client certificate private key
    :param xroad_client_cert: Client certificate file (uploaded to X-Road
    server)
    :param verify: Verify server TLS/SSL
    :param api_key: SAPA API key
    :param file: File to send
    :param package_checksum: boolean, calculate and add checksum of package
    :param package_type: SAPA package type
    :param ahaa_series_id: SAPA AHAA Series ID
    :param transfer_oid: SAPA Transfer ID
    :param email_notify_to: Email to notify when package is processed
    :param digitization_rationale: UUID if package is a digitization package
    """

    if os.path.exists(file) is False:
        click.echo('File ' + file + ' not found')
        sys.exit(0)

    headers = {'X-Road-Client': xroad_client.lstrip('/')}
    if api_key is not None:
        headers['X-Api-Key'] = api_key

    metadata = {'filename': os.path.basename(file)}
    if package_checksum:
        metadata['package_checksum'] = md5_file(file)
    if package_type is not None:
        metadata['package_type'] = package_type
    if ahaa_series_id is not None:
        metadata['ahaa_series_id'] = ahaa_series_id
    if transfer_oid is not None:
        metadata['transfer_oid'] = transfer_oid
    if email_notify_to is not None:
        metadata['email_notify_to'] = email_notify_to
    if digitization_rationale is not None:
        metadata['digitization_rationale'] = digitization_rationale

    opts = {'headers': headers}
    if os.path.exists(xroad_client_cert) and os.path.exists(xroad_client_key):
        opts['client_cert'] = (xroad_client_cert, xroad_client_key)
    else:
        click.echo('Client certificate and key not used (not found).',
                   file=sys.stderr)

    tus_client = client.TusClient(target_url, **opts)

    uploader = tus_client.uploader(file,
                                   metadata=metadata,
                                   chunk_size=1048576,
                                   verify_tls_cert=verify)
    try:
        uploader.upload()
        click.echo('Upload complete')
    except Exception as e:
        click.echo(type(e))
        click.echo(e.args)


if __name__ == '__main__':
    RETVAL = main()  # pylint: disable=no-value-for-parameter
    sys.exit(RETVAL)
