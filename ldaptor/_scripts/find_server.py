import sys
from ldaptor.protocols.ldap.distinguishedname import DistinguishedName
from twisted.internet.defer import DeferredList
from twisted.internet import reactor
from twisted.names import client, dns


def printAnswer(answers, dn):
    for rrlist in answers:
        for rr in rrlist:
            if isinstance(rr.payload, dns.Record_SRV):
                print(
                    "%s\tpri=%d weight=%d %s:%d"
                    % (
                        dn,
                        rr.payload.priority,
                        rr.payload.weight,
                        rr.payload.target,
                        rr.payload.port,
                    )
                )
            else:
                # suppress additional records
                pass
    return answers


exitStatus = 0


def errback(data):
    print("ERROR:", data.getErrorMessage())
    global exitStatus
    exitStatus = 1


def main(dns):
    l = []
    resolver = client.Resolver("/etc/resolv.conf")

    for dnString in dns:
        dn = DistinguishedName(stringValue=dnString)
        domain = dn.getDomainName()

        d = resolver.lookupService("_ldap._tcp.%s" % domain)
        l.append(d)
        d.addCallback(printAnswer, dnString)
        d.addErrback(errback)
    dl = DeferredList(l)
    dl.addBoth(lambda dummy: reactor.callLater(0, reactor.stop))
    reactor.run()
    sys.exit(exitStatus)


def console_script():
    if not sys.argv[1:]:
        print("%s: usage:" % sys.argv[0], file=sys.stderr)
        print("  %s DN.." % sys.argv[0], file=sys.stderr)
    else:
        main(sys.argv[1:])


if __name__ == "__main__":
    sys.exit(console_script())
