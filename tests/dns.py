# created based off of Chatgpt
import asyncio
import aiodns

async def resolve_dns(domain_name):
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

    return {
        "A": a_result,
        "MX": mx_result,
        "TXT": txt_result
    }

async def handle_client(reader, writer):
    data = await reader.read(100)
    domain_name = data.decode().strip()
    print(f"Received domain name: {domain_name}")

    # Resolve the DNS for A, MX, and TXT records
    dns_results = await resolve_dns(domain_name)
    
    response = f"DNS results for {domain_name}:\n"
    response += f"A Records: {dns_results['A']}\n"
    response += f"MX Records: {dns_results['MX']}\n"
    response += f"TXT Records: {dns_results['TXT']}\n"

    writer.write(response.encode())
    await writer.drain()

    print("Closing the connection")
    writer.close()
    await writer.wait_closed()

async def main():
    server = await asyncio.start_server(
        handle_client, '127.0.0.1', 8888)

    addr = server.sockets[0].getsockname()
    print(f'Serving on {addr}')

    async with server:
        await server.serve_forever()

asyncio.run(main())