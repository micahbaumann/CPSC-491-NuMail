import aiodns
import asyncio
import ast
import ipaddress

from errors.nuerrors import NuMailError
from config.config import server_settings

async def resolve_dns(domain_name: str, records: list = ["MX"], timeout: float | int = float(server_settings["dns_timeout"])):
    resolver = aiodns.DNSResolver()

    ret = {}
    
    for record in records:
        try:
            # Resolve MX records (Mail Exchange servers)
            if record == "MX" or record == "TXT" or record == "A" or record == "AAAA" or record == "CNAME" or record == "NAPTR" or record == "NS" or record == "PTR" or record == "SOA" or record == "SRV":
                resolved_records = await asyncio.wait_for(resolver.query(domain_name, record), timeout)

            if record == "MX":
                ret[record] = [{"host": entry.host, "priority": entry.priority, "ttl": entry.ttl} for entry in resolved_records]
            elif record == "TXT":
                ret[record] = [{"text": entry.text, "ttl": entry.ttl} for entry in resolved_records]
            elif record == "A" or record == "AAAA":
                ret[record] = [{"host": entry.host, "ttl": entry.ttl} for entry in resolved_records]
            elif record == "CNAME":
                ret[record] = [{"cname": entry.cname, "ttl": entry.ttl} for entry in resolved_records]
            elif record == "NAPTR":
                ret[record] = [{"order": entry.order, "preference": entry.preference, "flags": entry.flags, "service": entry.service, "regex": entry.regex, "replacement": entry.replacement, "ttl": entry.ttl} for entry in resolved_records]
            elif record == "NS":
                ret[record] = [{"host": entry.host, "ttl": entry.ttl} for entry in resolved_records]
            elif record == "PTR":
                ret[record] = [{"name": entry.cname, "ttl": entry.ttl} for entry in resolved_records]
            elif record == "SOA":
                ret[record] = [{"nsmane": entry.nsmane, "hostmaster": entry.hostmaster, "serial": entry.serial, "refresh": entry.refresh, "retry": entry.retry, "expires": entry.expires, "minttl": entry.minttl, "ttl": entry.ttl} for entry in resolved_records]
            elif record == "SRV":
                ret[record] = [{"host": entry.host, "port": entry.port, "priority": entry.priority, "ttl": entry.ttl} for entry in resolved_records]
                
        except aiodns.error.DNSError as e:
            if ast.literal_eval(str(e))[0] == 4:
                raise NuMailError(code="7.7.2", message=f"NuMail DNS resolver error, \"{e}\"" )
            elif ast.literal_eval(str(e))[0] == 1:
                raise NuMailError(code="7.7.3", message=f"NuMail DNS resolver error, \"{e}\"" )
            elif ast.literal_eval(str(e))[0] == 12:
                raise NuMailError(code="7.7.4", message=f"NuMail DNS resolver error, \"connection timed out\"" )
            else:
                raise NuMailError(code="7.7.1", message=f"NuMail DNS resolver error, \"{e}\"" )
        except TimeoutError:
            raise NuMailError(code="7.7.4", message=f"NuMail DNS resolver error, \"connection timed out\"" )
        except Exception as e:
            raise NuMailError(code="7.7.0", message=f"NuMail DNS resolver error, \"{e}\"" )

    return ret

def is_ip(ip: str) -> bool:
    try:
        ipaddress.ip_address(ip)
        return True
    except:
        return False