# Take wg0.conf and move it into /etc/wireguard/

# Change <server-private-key> and <client-public-key> to the actual keys using the values inside 
# server-private.key and client-public.key

# Read the keys from the files
server_private_key=$(cat ./server-private.key)
client_public_key=$(cat ./client-public.key)

# Replace placeholders in wg0.conf with actual keys
sed -i "s|<server-private-key>|$server_private_key|g" ./wg0.conf
sed -i "s|<client-public-key>|$client_public_key|g" ./wg0.conf

# Move wg0.conf to /etc/wireguard/
sudo mv ./wg0.conf /etc/wireguard/