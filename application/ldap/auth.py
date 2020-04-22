import base64
import ldap

from application.utils import get_logger

logger = get_logger()


class Auth:
    def __init__(self, headers):
        # fmt: off
        self.authorization = headers.get("Authorization",       None)
        self.bind_dn       = headers.get("X-Ldap-BindDN",       "cn=admin,dc=lnls,dc=br")
        self.bind_pass     = headers.get("X-Ldap-BindPass",     None)
        self.group_base_dn = headers.get("X-Ldap-Group-BaseDN", "ou=epics-archiver,ou=groups,dc=lnls,dc=br")
        self.group_cns     = headers.get("X-Ldap-Group-CNs",    "cn=archiver-admins").split(",")
        self.realm         = headers.get("X-Ldap-Realm",        "EPICS Archiver - MGMT Actions")
        self.starttls      = headers.get("X-Ldap-Starttls",     "false")
        self.url           = headers.get("X-Ldap-URL",          "ldap://10.0.38.42:389")
        self.user_base_dn  = headers.get("X-Ldap-User-BaseDN",  "ou=users,dc=lnls,dc=br")
        # fmt: on

    def get_user_pass(self):

        if self.authorization is None:
            raise Exception("No Authorization header!")

        if not self.authorization.lower().startswith("basic "):
            raise Exception("Invalid Authorization header!")

        logger.debug("decoding credentials")

        try:
            auth_decoded = base64.b64decode(self.authorization[6:])
            auth_decoded = auth_decoded.decode("utf-8")
            user, passwd = auth_decoded.split(":", 1)
            return user, passwd

        except:
            raise Exception(
                "Failed to get information from Authorization header. {}".format(
                    self.authorization
                )
            )

    def authenticate(self):
        try:
            user, passw = self.get_user_pass()

            l = ldap.initialize(self.url)
            l.protocol_version = ldap.VERSION3
            l.set_option(ldap.OPT_NETWORK_TIMEOUT, 5.0)

            if self.starttls == "true":
                l.start_tls_s()

            # See https://www.python-ldap.org/en/latest/faq.html
            # if ctx['disable_referrals'] == 'true':
            #   l.set_option(ldap.OPT_REFERRALS, 0)

            logger.debug("binding as search user")
            l.bind_s(self.bind_dn, self.bind_pass, ldap.AUTH_SIMPLE)

            logger.debug("preparing search filter")
            searchfilter = "(cn={})".format(user)

            logger.debug(
                ('searching on server "%s" with base dn ' + '"%s" with filter "%s"')
                % (self.url, self.user_base_dn, searchfilter)
            )

            logger.info(
                "running user search query {} with filter {}".format(
                    self.user_base_dn, searchfilter
                )
            )
            results = l.search_s(
                self.user_base_dn, ldap.SCOPE_SUBTREE, searchfilter, ["objectclass"], 1
            )

            logger.debug("verifying search query results")
            nres = len(results)

            if nres < 1:
                logger.warn("no user objects found")
                return False

            if nres > 1:
                logger.warn(
                    "note: filter match multiple user objects: %d, using first" % nres
                )

            user_entry = results[0]
            ldap_dn = user_entry[0]

            if ldap_dn == None:
                logger.warn("matched object has no dn")
                return False

            # Check if user in groups
            logger.info('Required groups: "{}"'.format(ldap_dn, self.group_cns))

            # Include check of groups
            for gcn in self.group_cns:
                res = l.search_s(
                    self.group_base_dn,
                    ldap.SCOPE_ONELEVEL,
                    "(&({}))".format(gcn),
                    ["member"],
                )

                logger.debug(
                    "check if {} is member of {},{}".format(
                        ldap_dn, gcn, self.group_base_dn
                    )
                )
                if "{}".format(ldap_dn).encode("utf-8") not in res[0][1]["member"]:
                    raise Exception("user do not belong to group")

            logger.debug('attempting to bind using dn "%s"' % (ldap_dn))
            l.bind_s(ldap_dn, passw, ldap.AUTH_SIMPLE)

            return True
        except:
            logger.exception("Failed to authenticate")
            return False
