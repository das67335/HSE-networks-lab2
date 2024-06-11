import re
import subprocess
import sys
import urllib.request

# to exceed max MTU
START_MTU = 9500
TIMEOUT_SEC = 1.


def validate_host(host: str) -> bool:
    ipaddr = r"^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$"
    hostname = r"^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9])$"
    return re.match(ipaddr, host) or re.match(hostname, host)


def test_ping(host: str) -> bool:
    try:
        result = subprocess.run(
            ["ping", host, "-c", "1", "-W", str(TIMEOUT_SEC)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        return result.returncode == 0
    except Exception as e:
        raise RuntimeError(f"Error checking host availability: {e}")


def test_http(host: str) -> bool:
    try:
        urllib.request.urlopen(f"http://{host}", timeout=TIMEOUT_SEC)
        return True
    except Exception:
        return False


def find_mtu(host: str) -> int:
    # 20 bytes IP header + 8 bytes ICMP header
    headers = 28
    mtu = START_MTU
    while True:
        result = subprocess.run(
            ["ping", host, "-c", "1", "-M", "do", "-s",
                str(mtu - headers), "-W", str(TIMEOUT_SEC)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        if result.returncode == 0:
            return mtu
        output = result.stderr.decode() + result.stdout.decode()
        mtu_match1 = re.search(
            r"Frag needed and DF set \(mtu = (\d+)\)", output)
        mtu_match2 = re.search(
            r"ping: local error: message too long, mtu=(\d+)", output)
        if mtu_match1:
            mtu = int(mtu_match1.group(1))
        elif mtu_match2:
            mtu = int(mtu_match2.group(1))
        else:
            msg = "ICMP packets are partially blocked"
            if mtu != START_MTU:
                msg += f"; MTU reported by the last successful ping is {mtu} bytes"
            print(msg)
            return -1


def main():
    host = input("Enter the host: ")
    if not validate_host(host):
        print(
            f"Invalid host: \"{host}\". Please enter a valid IP address or hostname.")
        return
    if not test_ping(host):
        if test_http(host):
            print(f"ICMP is blocked, but HTTP is available")
        else:
            print(f"Host \"{host}\" is not available")
        return

    if (mtu := find_mtu(host)) != -1:
        print(f"MTU is {mtu} bytes")


if __name__ == "__main__":
    print("To interrupt the program, press Ctrl+C.")
    while True:
        try:
            main()
            print()  # additional newline
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            sys.exit(1)
