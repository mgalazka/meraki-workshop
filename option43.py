# list of controllers
cont = ["10.36.30.6"]

# start our option43 string
option43="f1:"

# determine length value and append to option43 string
hexlength = str(hex((len(cont)*4))).replace("0x","")
if len(hexlength)<2:
    hexlength = "0"+hexlength
option43+=hexlength+":"

# calculate all of the controller hex IPs
for c in cont:
    contsplit = c.split(".")
    for n in contsplit:
        buffer=str(hex(int(n))).replace("0x","")
        if(len(buffer)) < 2:
            buffer="0"+buffer
        option43+=buffer+":"

# print the option 43 value to use with Meraki

print(f"Configure Meraki DHCP Option, Custom, code 43, hex, {option43[0:-1].upper()}")

