import os

bin_filename = "Tomba! (USA).bin"
iso_filename = "Tomba_extracted.iso"

# Sector configurations for MODE2/2352
RAW_SECTOR_SIZE = 2352
USER_DATA_START = 24  # Skip the 12-byte Sync + 4-byte Header + 8-byte Subheader
USER_DATA_SIZE = 2048  # The size of actual usable data per sector

if not os.path.exists(bin_filename):
    print(f"Error: Could not find '{bin_filename}' in the current folder.")
else:
    print(f"Converting {bin_filename} to a standard ISO...")

    with open(bin_filename, "rb") as bin_file, open(iso_filename, "wb") as iso_file:
        while True:
            # Read one full raw sector
            sector = bin_file.read(RAW_SECTOR_SIZE)
            if not sector:
                break  # End of file reached

            # Extract just the 2048 bytes of user data
            user_data = sector[USER_DATA_START : USER_DATA_START + USER_DATA_SIZE]

            # Write it out to the clean ISO file
            iso_file.write(user_data)

    print(f"Success! Saved clean data to '{iso_filename}'.")
