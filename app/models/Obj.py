class RegrasFirewall():
    def __init__(self, dpid, id,src, dst, protocol, permission):
        self.dpid = dpid
        self.id = id
        self.src = self.netmask_prefix(src)
        self.dst = self.netmask_prefix(dst)
        self.protocol = protocol
        self.permission = permission

    def netmask_prefix(self, address):
        if address != 'any':
            ip = address.split("/")[0]
            vet_mask = address.split("/")[1].split(".")
            prefix = 0
            for oct in vet_mask:
                if int(oct) == 255:
                    prefix += 8
                elif int(oct) > 0 and int(oct) < 255:
                    b = bin(int(oct)).split("b")[1].count("1")
                    prefix += b
            addr = "%s/%s" %(ip,prefix)
            return addr
        else:
            return address
