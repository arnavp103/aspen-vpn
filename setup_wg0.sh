# Take wg0.conf and move it into /etc/wireguard/

# Change <server-private-key> and <client-public-key> to the actual keys using the values inside 
# server-private.key and client-public.key


if [ "$1" != "client" ] && [ "$1" != "server" ]; then
    echo "Usage: $0 {client|server}"
    exit 1
fi


# If arg is server, move server-private.key to /etc/wireguard/

if [ "$1" == "server" ]; then
    # Read the keys from the files
    server_private_key=$(cat ./server-private.key)
    client_public_key=$(cat ./client-public.key)

    # Replace placeholders in wg0.conf with actual keys
    sed -i "s|<server-private-key>|$server_private_key|g" ./wg0s/server/wg0.conf
    sed -i "s|<client-public-key>|$client_public_key|g" ./wg0s/server/wg0.conf

    # Move wg0.conf to /etc/wireguard/
    sudo mv ./wg0s/server/wg0.conf /etc/wireguard/
    echo "Type Server - Moved wg0.conf to /etc/wireguard/"
fi

# If arg is client, move client-private.key to /etc/wireguard/

# Check that server-ip is set as arg
if [ "$1" == "client" ] && [ -z "$2" ]; then
    echo "Usage: $0 client <server-ip>"
    exit 1
fi

if [ "$1" == "client" ]; then
    # <client-private-key>, <server-public-key>, <server-ip>

    # Read the keys from the files
    client_private_key=$(cat ./client-private.key)
    server_public_key=$(cat ./server-public.key)


    # Replace placeholders in wg0.conf with actual keys
    sed -i "s|<client-private-key>|$client_private_key|g" ./wg0s/client/wg0.conf
    sed -i "s|<server-public-key>|$server_public_key|g" ./wg0s/client/wg0.conf
    sed -i "s|<server-ip>|$2|g" ./wg0s/client/wg0.conf

    # Move wg0.conf to /etc/wireguard/
    sudo mv ./wg0s/client/wg0.conf /etc/wireguard/
    echo "Type Client - Moved wg0.conf to /etc/wireguard/"
fi