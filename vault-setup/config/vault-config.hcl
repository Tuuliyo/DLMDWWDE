# ------------------------------------------------------------------------------
# Vault Configuration File
# This file configures the Vault server to use a file storage backend and sets up
# a TCP listener for API communication. It also disables mlock for systems where
# mlock is not supported and enables the Vault UI for ease of access.
# ------------------------------------------------------------------------------

# Storage backend configuration
# Specifies the file system as the storage backend for Vault.
# The data will be stored in the specified `path`.
storage "file" {
    path = "./data"  # Directory to store Vault data on the local filesystem
}

# Listener configuration
# Configures a TCP listener for Vault to communicate with clients.
listener "tcp" {
    address     = "0.0.0.0:8200"  # Listen on all network interfaces on port 8200
    tls_disable = true            # Disable TLS for development purposes (not secure for production)
}

# Global settings
disable_mlock = true  # Disable mlock syscall for systems where it is not supported
ui            = true  # Enable the Vault UI for web-based interaction
api_addr      = "http://0.0.0.0:8200"  # API address for Vault server communication
