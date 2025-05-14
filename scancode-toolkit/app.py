from flask import Flask, jsonify, request

app = Flask(__name__)

# JSON data
json_data = {
    "projectName": "MRI scanner",
    "reportDate": "2024-07-02T13:40:29.433905630Z",
    "vulnerabilities": [
        {
            "fileName": "bootstrap.min.js",
            "vulnerabilityId": "CVE-2016-10735",
            "description": "In Bootstrap 3.x before 3.4.0 and 4.x-beta before 4.0.0-beta.2, XSS is possible in the data-target attribute, a different vulnerability than CVE-2018-14041.",
            "type": "Cross-Site Scripting (XSS)"
        },
        {
            "fileName": "bootstrap.min.js",
            "vulnerabilityId": "CVE-2018-14041",
            "description": "In Bootstrap before 4.1.2, XSS is possible in the data-target property of scrollspy.",
            "type": "Cross-Site Scripting (XSS)"
        },
        {
            "fileName": "bootstrap.min.js",
            "vulnerabilityId": "CVE-2018-14042",
            "description": "In Bootstrap before 4.1.2, XSS is possible in the data-container property of tooltip.",
            "type": "Cross-Site Scripting (XSS)"
        },
        {
            "fileName": "bootstrap.min.js",
            "vulnerabilityId": "CVE-2018-20676",
            "description": "In Bootstrap before 3.4.0, XSS is possible in the tooltip data-viewport attribute.",
            "type": "Cross-Site Scripting (XSS)"
        },
        {
            "fileName": "bootstrap.min.js",
            "vulnerabilityId": "CVE-2018-20677",
            "description": "In Bootstrap before 3.4.0, XSS is possible in the affix configuration target property.",
            "type": "Cross-Site Scripting (XSS)"
        },
        {
            "fileName": "bootstrap.min.js",
            "vulnerabilityId": "CVE-2019-8331",
            "description": "In Bootstrap before 3.4.1 and 4.3.x before 4.3.1, XSS is possible in the tooltip or popover data-template attribute.",
            "type": "Cross-Site Scripting (XSS)"
        },
        {
            "fileName": "bootstrap.min.js",
            "vulnerabilityId": "Bootstrap before 4.0.0 is end-of-life and no longer maintained.",
            "description": "Bootstrap before 4.0.0 is end-of-life and no longer maintained.",
            "type": "Unsupported Version"
        },
        {
            "fileName": "commons-compress-1.21.jar",
            "vulnerabilityId": "CVE-2024-25710",
            "description": "Loop with Unreachable Exit Condition ('Infinite Loop') vulnerability in Apache Commons Compress.This issue affects Apache Commons Compress: from 1.3 through 1.25.0.",
            "type": "Resource Exhaustion"
        },
        {
            "fileName": "commons-compress-1.21.jar",
            "vulnerabilityId": "CVE-2024-26308",
            "description": "Allocation of Resources Without Limits or Throttling vulnerability in Apache Commons Compress.This issue affects Apache Commons Compress: from 1.21 before 1.26.",
            "type": "Resource Exhaustion"
        },
        {
            "fileName": "commons-text-1.9.jar",
            "vulnerabilityId": "CVE-2022-42889",
            "description": "Apache Commons Text performs variable interpolation, allowing properties to be dynamically evaluated and expanded. The standard format for interpolation is \"${prefix:name}\", where \"prefix\" is used to locate an instance of org.apache.commons.text.lookup.StringLookup that performs the interpolation. Starting with version 1.5 and continuing through 1.9, the set of default Lookup instances included interpolators that could result in arbitrary code execution or contact with remote servers. These lookups are: - \"script\" - execute expressions using the JVM script execution engine (javax.script) - \"dns\" - resolve dns records - \"url\" - load values from urls, including from remote servers Applications using the interpolation defaults in the affected versions may be vulnerable to remote code execution or unintentional contact with remote servers if untrusted configuration values are used. Users are recommended to upgrade to Apache Commons Text 1.10.0, which disables the problematic interpolators by default.",
            "type": "Execution Vulnerability"
        },
        {
            "fileName": "gson-2.8.5.jar",
            "vulnerabilityId": "CVE-2022-25647",
            "description": "The package com.google.code.gson:gson before 2.8.9 are vulnerable to Deserialization of Untrusted Data via the writeReplace() method in internal classes, which may lead to DoS attacks.",
            "type": "Execution Vulnerability"
        },
        {
            "fileName": "guava-31.0.1-jre.jar",
            "vulnerabilityId": "CVE-2023-2976",
            "description": "Use of Java's default temporary directory for file creation in `FileBackedOutputStream` in Google Guava versions 1.0 to 31.1 on Unix systems and Android Ice Cream Sandwich allows other users and apps on the machine with access to the default Java temporary directory to be able to access the files created by the class.",
            "type": "Execution Vulnerability"
        },
        {
            "fileName": "guava-31.0.1-jre.jar",
            "vulnerabilityId": "CVE-2020-8908",
            "description": "A temp directory creation vulnerability exists in all versions of Guava, allowing an attacker with access to the machine to potentially access data in a temporary directory created by the Guava API com.google.common.io.Files.createTempDir(). By default, on unix-like systems, the created directory is world-readable (readable by an attacker with access to the system). The method in question has been marked @Deprecated in versions 30.0 and later and should not be used. For Android developers, we recommend choosing a temporary directory API provided by Android, such as context.getCacheDir(). For other Java developers, we recommend migrating to the Java 7 API java.nio.file.Files.createTempDirectory() which explicitly configures permissions of 700, or configuring the Java runtime's java.io.tmpdir system property to point to a location whose permissions are appropriately configured.",
            "type": "Execution Vulnerability"
        },
        {
            "fileName": "h2-2.1.210.jar",
            "vulnerabilityId": "CVE-2022-45868",
            "description": "The web-based admin console in H2 Database Engine before 2.2.220 can be started via the CLI with the argument -webAdminPassword, which allows the user to specify the password in cleartext for the web admin console. Consequently, a local user (or an attacker that has obtained local access through some means) would be able to discover the password by listing processes and their arguments. NOTE: the vendor states \"This is not a vulnerability of H2 Console ... Passwords should never be passed on the command line and every qualified DBA or system administrator is expected to know that.\" Nonetheless, the issue was fixed in 2.2.220.",
            "type": "Execution Vulnerability"
        },
        {
            "fileName": "h2-2.1.210.jar",
            "vulnerabilityId": "CVE-2018-14335",
            "description": "h2database - Improper Link Resolution Before File Access",
            "type": "Execution Vulnerability"
        },
        {
            "fileName": "jackson-databind-2.13.1.jar",
            "vulnerabilityId": "CVE-2020-36518",
            "description": "jackson-databind before 2.13.0 allows a Java StackOverflow exception and denial of service via a large depth of nested objects.",
            "type": "Resource Exhaustion"
        },
        {
            "fileName": "jackson-databind-2.13.1.jar",
            "vulnerabilityId": "CVE-2022-42003",
            "description": "In FasterXML jackson-databind before versions 2.13.4.1 and 2.12.17.1, resource exhaustion can occur because of a lack of a check in primitive value deserializers to avoid deep wrapper array nesting, when the UNWRAP_SINGLE_VALUE_ARRAYS feature is enabled.",
            "type": "Resource Exhaustion"
        },
        {
            "fileName": "jackson-databind-2.13.1.jar",
            "vulnerabilityId": "CVE-2022-42004",
            "description": "In FasterXML jackson-databind before 2.13.4, resource exhaustion can occur because of a lack of a check in BeanDeserializer._deserializeFromArray to prevent use of deeply nested arrays. An application is vulnerable only with certain customized choices for deserialization.",
            "type": "Resource Exhaustion"
        },
        {
            "fileName": "jackson-databind-2.13.1.jar",
            "vulnerabilityId": "CVE-2023-35116",
            "description": "jackson-databind through 2.15.2 allows attackers to cause a denial of service or other unspecified impact via a crafted object that uses cyclic dependencies. NOTE: the vendor's perspective is that this is not a valid vulnerability report, because the steps of constructing a cyclic data structure and trying to serialize it cannot be achieved by an external attacker.",
            "type": "Resource Exhaustion"
        },
        {
            "fileName": "jquery.dataTables-1.10.22.min.js",
            "vulnerabilityId": "prototype pollution",
            "description": "prototype pollution",
            "type": "Prototype Pollution"
        },
        {
            "fileName": "jquery.dataTables-1.10.22.min.js",
            "vulnerabilityId": "CVE-2021-23445",
            "description": "This affects the package datatables.net before 1.11.3. If an array is passed to the HTML escape entities function it would not have its contents escaped.",
            "type": "Cross-Site Scripting (XSS)"
        },
        {
            "fileName": "jquery.dataTables-1.10.22.min.js",
            "vulnerabilityId": "possible XSS",
            "description": "possible XSS",
            "type": "Cross-Site Scripting (XSS)"
        },
        {
            "fileName": "jquery.dataTables.min.js",
            "vulnerabilityId": "CVE-2020-28458",
            "description": "All versions of package datatables.net are vulnerable to Prototype Pollution due to an incomplete fix for https://snyk.io/vuln/SNYK-JS-DATATABLESNET-598806.",
            "type": "Prototype Pollution"
        },
        {
            "fileName": "jquery.dataTables.min.js",
            "vulnerabilityId": "CVE-2021-23445",
            "description": "This affects the package datatables.net before 1.11.3. If an array is passed to the HTML escape entities function it would not have its contents escaped.",
            "type": "Cross-Site Scripting (XSS)"
        },
        {
            "fileName": "jquery.dataTables.min.js",
            "vulnerabilityId": "CVE-2015-6584",
            "description": "Cross-site scripting (XSS) vulnerability in the DataTables plugin 1.10.8 and earlier for jQuery allows remote attackers to inject arbitrary web script or HTML via the scripts parameter to media/unit_testing/templates/6776.php.",
            "type": "Cross-Site Scripting (XSS)"
        },
        {
            "fileName": "jquery.dataTables.min.js",
            "vulnerabilityId": "prototype pollution",
            "description": "prototype pollution",
            "type": "Prototype Pollution"
        },
        {
            "fileName": "jquery.dataTables.min.js",
            "vulnerabilityId": "possible XSS",
            "description": "possible XSS",
            "type": "Cross-Site Scripting (XSS)"
        },
        {
            "fileName": "jquery.min.js",
            "vulnerabilityId": "CVE-2015-9251",
            "description": "jQuery before 3.0.0 is vulnerable to Cross-site Scripting (XSS) attacks when a cross-domain Ajax request is performed without the dataType option, causing text/javascript responses to be executed.",
            "type": "Cross-Site Scripting (XSS)"
        },
        {
            "fileName": "jquery.min.js",
            "vulnerabilityId": "CVE-2019-11358",
            "description": "jQuery before 3.4.0, as used in Drupal, Backdrop CMS, and other products, mishandles jQuery.extend(true, {}, ...) because of Object.prototype pollution. If an unsanitized source object contained an enumerable __proto__ property, it could extend the native Object.prototype.",
            "type": "Prototype Pollution"
        },
        {
            "fileName": "jquery.min.js",
            "vulnerabilityId": "CVE-2020-11022",
            "description": "In jQuery versions greater than or equal to 1.2 and before 3.5.0, passing HTML from untrusted sources - even after sanitizing it - to one of jQuery's DOM manipulation methods (i.e. .html(), .append(), and others) may execute untrusted code. This problem is patched in jQuery 3.5.0.",
            "type": "Cross-Site Scripting (XSS)"
        },
        {
            "fileName": "jquery.min.js",
            "vulnerabilityId": "CVE-2020-11023",
            "description": "In jQuery versions greater than or equal to 1.0.3 and before 3.5.0, passing HTML containing <option> elements from untrusted sources - even after sanitizing it - to one of jQuery's DOM manipulation methods (i.e. .html(), .append(), and others) may execute untrusted code. This problem is patched in jQuery 3.5.0.",
            "type": "Cross-Site Scripting (XSS)"
        },
        {
            "fileName": "jquery.min.js",
            "vulnerabilityId": "jQuery 1.x and 2.x are End-of-Life and no longer receiving security updates",
            "description": "jQuery 1.x and 2.x are End-of-Life and no longer receiving security updates",
            "type": "Unsupported Version"
        },
        {
            "fileName": "jsoup-1.14.3.jar",
            "vulnerabilityId": "CVE-2022-36033",
            "description": "jsoup is a Java HTML parser, built for HTML editing, cleaning, scraping, and cross-site scripting (XSS) safety. jsoup may incorrectly sanitize HTML including `javascript:` URL expressions, which could allow XSS attacks when a reader subsequently clicks that link. If the non-default `SafeList.preserveRelativeLinks` option is enabled, HTML including `javascript:` URLs that have been crafted with control characters will not be sanitized. If the site that this HTML is published on does not set a Content Security Policy, an XSS attack is then possible. This issue is patched in jsoup 1.15.3. Users should upgrade to this version. Additionally, as the unsanitized input may have been persisted, old content should be cleaned again using the updated version. To remediate this issue without immediately upgrading: - disable `SafeList.preserveRelativeLinks`, which will rewrite input URLs as absolute URLs - ensure an appropriate [Content Security Policy](https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP) is defined. (This should be used regardless of upgrading, as a defence-in-depth best practice.)",
            "type": "Cross-Site Scripting (XSS)"
        },
        {
            "fileName": "logback-core-1.2.10.jar",
            "vulnerabilityId": "CVE-2023-6378",
            "description": "A serialization vulnerability in logback receiver component part of ",
            "type": "Execution Vulnerability"
        }
    ]
}

@app.route('/vulnerabilitiesJson', methods=['POST'])
def get_json():
    request_data = request.get_json()
    if request_data and request_data.get('type') == 'mri (simulated r-pi)':
        return jsonify(json_data)
    else:
            return jsonify({
            "projectName": "MRI scanner",
            "reportDate": "2024-07-02T13:40:29.433905630Z",
            "vulnerabilities": []
        })
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5009)
