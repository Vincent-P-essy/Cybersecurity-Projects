#include <string.h>

struct pcap_if;

/* The help command must succeed even when interface discovery fails. */
int pcap_findalldevs(struct pcap_if **interfaces, char *error) {
    (void)interfaces;
    strcpy(error, "Interface discovery unavailable in this test");
    return -1;
}
