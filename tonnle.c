#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <pthread.h>

#define BUF_SIZE 10024

void *run(void *arg) {
    int client_socket = *((int *)arg);
    free(arg);

    char buffer[BUF_SIZE];
    int read_size;

    struct sockaddr_in server_addr;
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = inet_addr(argv[2]);
    server_addr.sin_port = htons(atoi(argv[3]));

    if (connect(client_socket, (struct sockaddr *)&server_addr, sizeof(server_addr)) == -1) {
        perror("[-]Error occurred during connect()\n");
        return NULL;
    }

    while ((read_size = read(client_socket, buffer, BUF_SIZE)) > 0) {
        write(client_socket, buffer, read_size);
    }

    close(client_socket);
    return NULL;
}

int main(int argc, char *argv[]) {
    if (argc != 5) {
        printf("[-]Usage : %s <local_port> <remote_host> <remote_port> <max_connections>\n", argv[0]);
        return -1;
    }

    int server_socket, client_socket;
    struct sockaddr_in server_addr, client_addr;
    socklen_t client_addr_size;

    server_socket = socket(PF_INET, SOCK_STREAM, 0);
    if (server_socket == -1) {
        perror("[-]Error occurred during socket()\n");
        return -1;
    }

    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = htonl(INADDR_ANY);
    server_addr.sin_port = htons(atoi(argv[1]));

    if (bind(server_socket, (struct sockaddr *)&server_addr, sizeof(server_addr)) == -1) {
        perror("[-]Error occurred during bind()\n");
        return -1;
    }

    if (listen(server_socket, atoi(argv[4])) == -1) {
        perror("[-]Error occurred during listen()\n");
        return -1;
    }

    while (1) {
        client_addr_size = sizeof(client_addr);
        client_socket = accept(server_socket, (struct sockaddr *)&client_addr, &client_addr_size);
        if (client_socket == -1) {
            perror("[-]Error occurred during accept()\n");
            continue;
        }

        printf("New client connected... IP : %s\n", inet_ntoa(client_addr.sin_addr));

        pthread_t thread;
        if (pthread_create(&thread, NULL, run, (void *)&client_socket) != 0) {
            perror("[-]Error occurred during pthread_create()\n");
            return -1;
        }

        pthread_detach(thread);
    }

    close(server_socket);
    return 0;
}