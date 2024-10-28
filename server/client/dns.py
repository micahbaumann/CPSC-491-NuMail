import aiodns

from errors.nuerrors import NuMailError

async def resolve_dns(domain_name, records: list = ["MX"]):
    resolver = aiodns.DNSResolver()
    
    try:
        # Resolve A records (IPv4 addresses)
        a_records = await resolver.query(domain_name, 'A')
        a_result = [entry.host for entry in a_records]
    except aiodns.error.DNSError as e:
        a_result = f"Failed to resolve A records: {e}"

    try:
        # Resolve MX records (Mail Exchange servers)
        mx_records = await resolver.query(domain_name, 'MX')
        mx_result = [(entry.priority, entry.host) for entry in mx_records]
    except aiodns.error.DNSError as e:
        mx_result = f"Failed to resolve MX records: {e}"

    try:
        # Resolve TXT records (Text records)
        txt_records = await resolver.query(domain_name, 'TXT')
        txt_result = [entry.text for entry in txt_records]
    except aiodns.error.DNSError as e:
        txt_result = f"Failed to resolve TXT records: {e}"

    ret = {}

    for record in records:
        ret[record] = []
        try:
            # Resolve records
            resolved_records = await resolver.query(domain_name, record)
            ret[record] = [entry.text for entry in resolved_records]
        except aiodns.error.DNSError as e:
            raise NuMailError(code="7.7.0", message="NuMail DNS resolver error")

    return ret