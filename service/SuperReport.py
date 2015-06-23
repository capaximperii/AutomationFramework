import os
import sys
import codecs
import pexpect


class SuperReport:
    """
    Constructor for the detailed test report.
    """
    def __init__(self, fmttag, rawtag, splitchar=":", data=""):
        self.fmttag =  fmttag
        self.rawtag =  rawtag
        self.data = data.replace(">"," &gt ")
        self.data = self.data.replace("<"," &lt ")
        self.fmt = ""
        self.splitchar = splitchar
    """
    Formats data into an html table for the report.
    """
    def formatHtmlTable(self):
        html = ""
        lines = self.data.split("\n")
        for l in lines:
            if len(l.strip()) > 0:
                if len(l.split(self.splitchar, 2)) == 2:
                    label = l.split(self.splitchar, 2)[0].strip()
                    prop = l.split(self.splitchar, 2)[1].strip()
                    html += """<tr><td class=label>%s</td><td class=property>%s</td></tr>\n""" %(label, prop)
                else:
                    html += """<tr><td class=label>%s</td><td class=property>%s</td></tr>\n""" %("no information", "N/A")
        self.fmt = html
    """
    Read file into the data buffer.
    """
    def fileToData(self, fpath):
        f = open(fpath, "r")
        lines = f.readlines()
        f.close()
        self.data = "".join(lines)
        self.data = self.data.replace(">"," &gt ")
        self.data = self.data.replace("<"," &lt ")
    """
    Read command output to data buffer.
    """
    def cmdToData(self, cmdline):
        self.data = pexpect.run(cmdline)
        self.data = self.data.replace(">"," &gt ")
        self.data = self.data.replace("<"," &lt ")
    """
    Convert raw data into html formatted buffer.
    """
    def dataToBuffer(self, template, html=True):
        if html:
            t = template.replace(self.fmttag, self.fmt)
        else:
            t = template.replace(self.rawtag, "\n<pre>" + self.data + "\n</pre>")
        return t

    """
    Write the data in buffer to file on disk.
    """
    @staticmethod
    def dataToFile(template, fname):
        f = codecs.open(fname, "w", "utf-8")
        f.write(template)
        f.close()

class CpuReport(SuperReport):
    #def __init__(self, fmttag,rawtag, splitchar=":"):
    #    CpuReport.__init__(self, fmttag, rawtag, splitchar)
    """
    Format CPU data into pretty table in the report.
    """
    def formatHtmlTable(self):
        print "Formatting table"
        html = ""
        lines = self.data.split("\n")
        for l in lines:
            if len(l.strip()) > 0:
                label = l.split(self.splitchar, 2)[0].strip()
                prop = l.split(self.splitchar, 2)[1].strip()
                if label.startswith("processor"):
                    label = "Processor"
                    html += """<br><br><h3><u>%s %s</u></h3><table><tr><th>Property</th><th>Value</th></tr>""" %(label, prop)
                else:
                    html += """<tr><td class=label>%s</td><td class=property>%s</td></tr>\n""" %(label, prop)
            else:
                html += "\n</table>"
        self.fmt = html

green_img = """<tr><td><img class="resultimg" src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA3XAAAN1wFCKJt4AAAAB3RJTUUH1wgCDAQ2+1qshAAABNlJREFUSMfVlltslEUUx3/zfXtjd9vthUuhhWIpUKgtFEm4GAQh4iWQIoqGxESCYCJRE30AxRgwPhgSReRJNDQYQ8ItRvBGFAxgJVQoS2lLuaWFQsP2xna7XXb3u8z4sFsstCH4YuIkk5PMTP6/mXPOnBn4vzfxoMmK1boTeA7BLCFYgKIcsBHUKckx4BRwOFhly38NqFitlwnB/rKJswoqSmYPK31kplY6bjYCwYUbNTS2nJY1DcfjTS3Bq0qyIlhlX3koQMVqXUOw0e/J2Liq8l3P5HHlor7tBLciV7kRbsLpcDMuZyoFWZOoKHyKmgtH5K6DnyfiyfgHwSp728MA3isqmPLhmmXrvZfbT3P04rco3UB3CDRdgAClQNkKJz6WlK0jPzCJ7Xs23bkRal4XrLK/Gain3yde4nF7d69dvsH787mvqW09jOaU6C6BwyXQXeIekGUbNNz8k2i8h8o5a5whu35p4QJZd+VI8lK/pjZAXEew75m5Lw5rajtFS3c9Qk+J6Q6B7kxBHB4tZZ2pMd0hCMdDTMt/ksqyt3WXR9u9efM/utqAAywaO7JoQt6IMaL64kGEEAgNhAaaLtAcAt2l4XRr6C4NTRcITVBWMI+tK4+R4cnhsfwl+D3Z3pO67/WhADPHjCh0XWo7iyXNQQHKHjYaIVLA/sn5xSvZvPQQPncAAKUUU3MX4vJqLw8CCMH8rMxcR3v4BqjUYqVSAV1cspYvKs8zM28ZZkIiLcULj77Pm0/sQNec2LaNbdtIKZk2/Flh9zkz+nUdA2Oc4Q3Qca0NJUBJ0HCybv42FpeuAuCN2Tu4cyzK3PErmFd0d5MYhoFpmkTjYZq7g4RaI1mDAQKZNJJIWyGFQtqwvOKdu+IADs3FhoUH7klrKSWJRIKb3Vf56sR6xmRNBJBDuEic7ehpI9OTi7RAWrDn5Kf83rD3gbUmFotRd62ajw++hGkbtHe1AdQMAkhbneiJdVpeVwDbUtimwkiYbPn+NX45uwsp7y03hmHQ29vL0fN7+eTQK0RiYbzOTLp62hMoqoeKwZnO7lCivGSGvznUiG3KdGZYfPbjOvruRHm6/NW7bjFNkwN/bWN/zVYsQ6Ljxu/OoTFcJ4HaQTd5dIXWkjTjz/szfXlZ/lzRFe5IA0BJRW3zEXTlJj9zMn2xKDuObuCn4E5sQyItKM6bTmf4ltXe3fZHcKe9ZRAgFFTkTRdHb4e71xZPKHaZlkG0ty+VrhKkrai7fpxk0uCH2i853fwb0gLbUgz3jyU7M4cLV85FLUMtaq9TfUPVIhEKqsiocpKRaPjxSRMnuzL8fnpjPZgJiZKgbLjUdoaOyE2kBZpyUlQwhdycXBoun4vFo8Zb57+1awA1JABwdDapel+BmezoCs3Jzgno4wvHC6/Pg9vtQtMFbpeb7EAOI4fnMX5sEb19EbupqTERCRkfNe6zv0uL2/2QgdVAA5yAD8gYVSZKR8/Qt/szvQW5IwOOjEy/7vN5kVLRF4vRF4nJ2509VjQcb71eLTdFWlUd0JvudwALUOK+E+iAG/ACPs1BXt50bYknwExvrpjq9IlRSqGMqOqKdaor8duqrqNB/Qq0Aj1ALC1u9l82McQDpKVBDsCV7h5gWBouAANIpm08bc30rmXaPeo/+VX8DYpbJ2hGIJ1EAAAAAElFTkSuQmCC"></td> """

red_img = """<tr><td><img class="resultimg" src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAABIAAAASABGyWs+AAAEl0lEQVRIx8WVW2xURRiAv5mzZ+/dbbttKYVKabFtioIxGNEg+gKRxCckQeLyRMKL4UXFd30xGqMhJt4So4GC0QdMvAUSMFEUIoFiJNCsUooW6LYU2u7ZPXs7M+PD2S5tIUQfjJP8OXPO+ef/5p/5L/AfD3Gvn4OwXsAzluQpbVhjDBFAW5KMNvyoDd8DX6bB/CvAIMQswT4rYO1Y0bss1NTeZCXbmok0J6kWiuQmbzE9MW3GRq4X3Jx7UWm2p+HKPwIMwkYp+Hzp8lRy9Ya1EVuVkMUcuA6i6EA4CrEEJtqAaUgxenbYG/51tKwNe9Pw/j0Bg9ArBUMPP9ofa+1qx4xdQrrTWAGBZQmE9FcYDVoZVCCC6Oon71T45fi5fNGtvJCG/XcFDIK0BOd6B+5b3dm9xDJXhglI4xu3RR2CqBn3DKrqP3X7SvIqyMljQ4429Kfh+pxdOY+0N94Q6VnWs9zyRjIIrREChAQpQVr4kIBAWgIp53l09TKxeIjuVR1hS3BwvgeytvsQ8NrA2vtj6voYVCsAxN7+jOhHR6G5beHBNrUR+vA44TcO1T+p0d/pGlhpB0L2I4OwcbEHa4LBQCUcjaCmJgEwxiBb2gk89Djhd79DJ9v8Y2loJfDON8jV6xCNKTBgDBjXxbh5WlLJALB+MWBdMhGztOtiNHWZ3bMdNZpBdvUS2vctXme/b3xFL+pKhsIrabQ2mJpoJ0+yMRayBE8uAEh4Ih6PRFTe8RW18S/yRpbZXVvqkMjHP9SN53dvQU1OohVoXZNCnmg8ioF1CwACltuWhS5XfUVVEw+8iSy5l3ZiKmVEMISplHFe3omXnfAjaE6UQZUqBKSFMTQuACg44ThFZQJBtDJ1UcpA4xIa3jpQNy6CIeJvHsA0ttXDVNX0jR0iP+sgBZnFd3A6l3cLxg7dNu4ZTGMbTfuPEOjuwxvJcPPZDXgjGQLdfSQ/OeJDah4oZcCOkJspGG04sRhwplAsh7UGTcDflWdoee8Qdk8f1UsZJp/bTOnCeSZ3bKY6ksHu6aP5gy/qutoDbYfJOW7BwMkFgDRcE8ZkJq7d0KJlSX2RNzVFaeg049s2URnP4lUNlfEs2W2bKJ3+GS87Xj8mEs0UHJdZxwU4drdS0Sdg6IGezqhddKDg1LNVSr9EiDntudg3Bq0By0Z2dPLbxcv5UtXbk4ZP5+xac5PDcHMrePlC8bFUW1sQBKZU8nPCmFqB43ZYKoNWYEJRZGs7V8cmKjm3dOp5eHF+0lvzX7bCqbLST8/M5lsSiUTQTiTQpTKmqmoJVauk2mCwEM0t6GgDI39lS5NOIfc1pC/AFPMa0HyAfRg6voJTy7WWMpd/EI2MNqeETDYiwhFMIIiIJ5BNKYgmmMmXGL6arV6oVodehdfPQBm/rpWByuJ+EAU6gKXA0n4Y2A27WmEZlqViwaBM2rZ0lWKmXNbG80QB3INw9Cc4C4wD2drzD6BwR8MBgjVAB9AKpCLQuhZ6V0FXJ3RMwOwIjJ+HP2/BDWAauIU/v4zfCyp3RNFdRhCIAzEgAoRr7hugCpRqkqvttsL/Mf4G3p1qg+fic5QAAAAZdEVYdFNvZnR3YXJlAHd3dy5pbmtzY2FwZS5vcmeb7jwaAAAAAElFTkSuQmCC"></td>"""

if __name__=='__main__':
    report = CpuReport("__CPUINFOFMT__", "__CPUINFORAW__", ":")
    report.fileToData("/proc/cpuinfo")
    report.formatHtmlTable()
    report.dataToFile("/tmp/out.html", "/tmp/out.html", True)
    report.dataToFile("/tmp/out.html", "/tmp/out.html", False)

    lspci = SuperReport("__LSPCI__", "__LSPCI__")
    lspci.cmdToData("lspci -v")
    lspci.dataToFile("/tmp/out.html", "/tmp/out.html", False)

    dmidecode = SuperReport("__DMIDECODE__", "__DMIDECODE__")
    dmidecode.cmdToData("dmidecode")
    dmidecode.dataToFile("/tmp/out.html", "/tmp/out.html", False)

    dmesg = SuperReport("__DMESG__", "__DMESG__")
    dmesg.cmdToData("dmesg")
    dmesg.dataToFile("/tmp/out.html", "/tmp/out.html", False)

    modules = SuperReport("__ETCMODULES__", "__ETCMODULES__")
    modules.cmdToData("cat /etc/modules")
    modules.dataToFile("/tmp/out.html", "/tmp/out.html", False)

    dmi = SuperReport("__DMI__", "__DMI__")
    dmi.cmdToData("find -L /sys/class/dmi")
    dmi.dataToFile("/tmp/out.html", "/tmp/out.html", False)

    lsmod = SuperReport("__LSMOD__", "__LSMOD__")
    lsmod.cmdToData("lsmod")
    lsmod.dataToFile("/tmp/out.html", "/tmp/out.html", False)

    modprobe = SuperReport("__MODPROBE__", "__MODPROBE__")
    modprobe.cmdToData("sh -c 'cat /etc/modprobe.d/*'")
    modprobe.dataToFile("/tmp/out.html", "/tmp/out.html", False)

    osinfo = SuperReport("__OSINFO__", "__OSINFO__", "=")
    osinfo.cmdToData("sh -c 'cat /etc/*-release'")
    osinfo.formatHtmlTable()
    osinfo.dataToFile("/tmp/out.html", "/tmp/out.html", True)

    pkginfo = SuperReport("__PKGINFO__", "__PKGINFO__", "-")
    pkginfo.cmdToData("rpm -qa")
    pkginfo.formatHtmlTable()
    pkginfo.dataToFile("/tmp/out.html", "/tmp/out.html", True)
