import argparse
import socket
import threading

# 端口映射配置信息
CFG_REMOTE_IP = '10.10.11.128'
CFG_REMOTE_PORT = 22
CFG_LOCAL_IP = '0.0.0.0'
CFG_LOCAL_PORT = 10022

# 接收数据缓存大小
PKT_BUFF_SIZE = 2048

# 调试日志封装
def send_log(content):
    print(content)
    return

# 单向流数据传递
def tcp_mapping_worker(conn_receiver, conn_sender):
    while True:
        try:
            data = conn_receiver.recv(PKT_BUFF_SIZE)
        except Exception:
            send_log('Event: Connection closed.')
            break

        if not data:
            send_log('Info: No more data is received.')
            break

        try:
            conn_sender.sendall(data)
        except Exception:
            send_log('Error: Failed sending data.')
            break

        # send_log('Info: Mapping data > %s ' % repr(data))
        send_log('Info: Mapping > %s -> %s > %d bytes.' % (conn_receiver.getpeername(), conn_sender.getpeername(), len(data)))

    conn_receiver.close()
    conn_sender.close()

    return

# 端口映射请求处理
def tcp_mapping_request(local_conn, remote_ip, remote_port):
    remote_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        remote_conn.connect((remote_ip, remote_port))
    except Exception:
        local_conn.close()
        send_log('Error: Unable to connect to the remote server.')
        return

    threading.Thread(target=tcp_mapping_worker, args=(local_conn, remote_conn)).start()
    threading.Thread(target=tcp_mapping_worker, args=(remote_conn, local_conn)).start()

    return

# 端口映射函数
def tcp_mapping(remote_ip, remote_port, local_ip, local_port):
    local_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    local_server.bind((local_ip, local_port))
    local_server.listen(5)

    send_log('Event: Starting mapping service on ' + local_ip + ':' + str(local_port) + ' ...')

    while True:
        try:
            (local_conn, local_addr) = local_server.accept()
        except KeyboardInterrupt:
            local_server.close()
            send_log('Event: Stop mapping service.')
            break

        threading.Thread(target=tcp_mapping_request, args=(local_conn, remote_ip, remote_port)).start()

        send_log('Event: Receive mapping request from %s:%d.' % local_addr)

    return

# 主函数
def main():
    parser = argparse.ArgumentParser(description='TCP Port Mapping Tool')
    parser.add_argument('remote_ip', help='Remote server IP address')
    parser.add_argument('remote_port', type=int, help='Remote server port')
    parser.add_argument('local_ip', help='Local IP address')
    parser.add_argument('local_port', type=int, help='Local port')
    args = parser.parse_args()

    tcp_mapping(args.remote_ip, args.remote_port, args.local_ip, args.local_port)

if __name__ == '__main__':
    main()