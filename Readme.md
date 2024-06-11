# Казимов Сулейман Патрисович

#### Запуск:

```
docker build . --tag find_mtu
docker run -it find_mtu
```

#### Пример работы:
```
To interrupt the program, press Ctrl+C.
Enter the host: 192.168.1.1
MTU is 1500 bytes

Enter the host: 192.168.1.2
Host "192.168.1.2" is not available

Enter the host: google.com
MTU is 1480 bytes

Enter the host: microsoft.com
ICMP packets are partially blocked; MTU reported by the last successful ping is 1480 bytes

Enter the host: aa bb
Invalid host: "aa bb". Please enter a valid IP address or hostname.

Enter the host: ^C⏎
```
