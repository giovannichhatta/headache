import re
from variables import issues_list

class Helpers:
    @staticmethod
    def is_insufficient_csp(csp_header):
        unsafe_csp_keywords = ["unsafe-eval", "unsafe-inline", "*", "data:"]
        issues = []
        insufficient = False
        csp_val = re.findall("(script|object)-src\s?([^;]+)", csp_header)
        csp_val = [' '. join([elem for elem in sublist]) for sublist in csp_val]
        csp_val = ' '.join(csp_val)
        
        if csp_val:
            if any(ele in csp_val for ele in unsafe_csp_keywords):
                issues.append("CSP contains dangerous keywords.")
                insufficient = True
            else:
                insufficient = False
        else:
            issues.append("script-src and/or object-src directive is missing.")
            insufficient = True

        return (insufficient, issues)

    @staticmethod
    def is_insufficient_hsts(hsts_header):
        min_age = 10368000
        max_age_val = int(re.search('max-age=(\d+);?', hsts_header)[1])
        issues = []
        insufficient = False

        if "includesubdomains" not in hsts_header:
            insufficient = True
            issues.append("Missing IncludeSubDomains")
        if max_age_val < min_age:
            insufficient = True
            issues.append("Max-age is shorter than 10368000")
        if "includesubdomains" in hsts_header and max_age_val >= min_age:
            insufficient = False

        return (insufficient, issues)

    @staticmethod
    def is_insufficient(domain, headers, temp, directive):
        issues = []
        header = headers[directive]

        if directive == "content-security-policy":
            csp = Helpers.is_insufficient_csp(header)
            temp[directive] = "Insufficient" if  csp[0] else "Present"
            issues.append(csp[1]) if csp[1] else ""
        elif directive == "strict-transport-security":
            hsts = Helpers.is_insufficient_hsts(header)
            temp[directive] = "Insufficient" if hsts[0] else "Present"
            issues.append(hsts[1]) if hsts[1] else ""

        if issues:
            issues_dict = {"domain" : domain}
        
            issues_dict["issues"] = issues
            issues_list.append(issues_dict)

    @staticmethod
    def parse_domain(domain):
        domain = domain.strip()
        domain = domain if domain[:4] == "http" else "https://" + domain

        return domain