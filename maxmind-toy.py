import geoip2.database
import geoip2.errors

ip = '1.1.1.1'

with geoip2.database.Reader('maxmind-local-db/GeoLite2-City.mmdb') as cityreader:
    response = cityreader.city(ip)
    print(response)
    print(response.country.name, response.subdivisions.most_specific.name, response.city.name)

with geoip2.database.Reader('maxmind-local-db/GeoLite2-ASN.mmdb') as asnreader:
    asnresponse = asnreader.asn(ip)
    print(asnresponse.autonomous_system_number)
    print(asnresponse.autonomous_system_organization)
    print(asnresponse.network)