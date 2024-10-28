import aiodns

from errors.nuerrors import NuMailError
from config.config import server_settings

async def resolve_dns(domain_name, records: list = ["MX"]):
    resolver = aiodns.DNSResolver()

    ret = {}
    
    for record in records:
        try:
            # Resolve MX records (Mail Exchange servers)
            resolved_records = await resolver.query(domain_name, record)
            ret[record] = [(entry.priority, entry.host) for entry in resolved_records]
        except aiodns.error.DNSError as e:
            raise NuMailError(code="7.7.0", message=f"NuMail DNS resolver error, \"{e}\"" )

    return ret