# ssl_checker.py
import ssl
import socket
import datetime
import concurrent.futures
from urllib.parse import urlparse

def get_ssl_info(domain):
    try:
        # Remove protocol if present
        domain = domain.replace('https://', '').replace('http://', '')
        # Remove path if present
        domain = domain.split('/')[0]
        
        context = ssl.create_default_context()
        
        with socket.create_connection((domain, 443), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
                
                # Extract certificate details
                not_after = datetime.datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                issuer = dict(x[0] for x in cert['issuer'])
                subject = dict(x[0] for x in cert['subject'])
                
                # Calculate days until expiration
                days_remaining = (not_after - datetime.datetime.now()).days
                
                return {
                    'domain': domain,
                    'status': 'valid',
                    'expires': not_after.strftime('%Y-%m-%d'),
                    'days_remaining': days_remaining,
                    'issuer': issuer.get('organizationName', 'Unknown'),
                    'subject': subject.get('commonName', domain),
                    'version': ssock.version(),
                    'error': None
                }
                
    except Exception as e:
        return {
            'domain': domain,
            'status': 'error',
            'expires': None,
            'days_remaining': None,
            'issuer': None,
            'subject': None,
            'version': None,
            'error': str(e)
        }

def check_multiple_domains(domains):
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_domain = {executor.submit(get_ssl_info, domain): domain for domain in domains}
        for future in concurrent.futures.as_completed(future_to_domain):
            result = future.result()
            results.append(result)
    return results