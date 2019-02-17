#!/usr/bin/env python3

################################################################################
# Import libraries
################################################################################
import re
from time import sleep
import requests
import random
from bs4 import BeautifulSoup
import os.path
import json

################################################################################
# Declare helper variables
################################################################################
base_url = 'https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfIVD/Detail.cfm?ID='

agents = ['Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
          'Mozilla/5.0 (X11; Linux i686; rv:64.0) Gecko/20100101 Firefox/64.0',
          'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246',
          'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1']

varnames = ['ManufacturerName', 'DateEffective', 'DocumentNumber',
            'TestName', 'TestType', 'ConsumerInfoPhoneNum',
            'ClassificationName', '510kNumber', 'DeviceName', 'Applicant',
            'ApplicantContact', 'Correspondent', 'CorrespondentContact',
            'RegulationNumber','ClassificationProductCode', 'DateReceived',
            'DateDecided', 'Decision', 'RegulationSpecialty', '510kReviewPanel',
            'Type', 'ReviewedByThirdParty', 'Combination'
]



varpatterns = ['Manufacturer Name', 'Effective Date', 'IVD Document Number',
             'Test Name', 'Test Type', 'Consumer Information Phone Number',
             'Device Classification Name', '510\(k\) Number', 'Device Name',
             'Applicant(?! Contact)', 'Application Contact',
             'Correspondent(?! Contact)',
             'Correspondent Contact', 'Regulation Number',
             'Classification Product Code', 'Date Received', 'Decision Date',
             'Decision(?! Date)', 'Regulation Medical Specialty', '510k Review Panel',
             'Type', 'Reviewed By Third Party', 'Combination Product'
]
varlabels = ['Manufacturer Name', 'Effective Date', 'IVD Document Number',
             'Test Name', 'Test Type', 'Consumer Information Phone Number',
             'Device Classification Name', '510\(k\) Number', 'Device Name',
             'Applicant', 'Application Contact',
             'Correspondent',
             'Correspondent Contact', 'Regulation Number',
             'Classification Product Code', 'Date Received', 'Decision Date',
             'Decision', 'Regulation Medical Specialty', '510k Review Panel',
             'Type', 'Reviewed By Third Party', 'Combination Product'
]


re_prefix = '(?:'
re_suffix = '\s*)(?:.*<.*\s*)*([^<>]*)'
re_strings = []

for label in varpatterns:
    re_strings.append(re_prefix + label + re_suffix)

outdir  = "data/"
outfile = "fda-ivd-data.txt"
outfile = os.path.join(outdir, outfile)
sep = "|"
ids = range(6593, 6594)

def scraper(base_url, agents):

    ############################################################################
    # This defines a scraper object to scrape the IVD data
    # We found the URL's all follow a simple pattern, so I loop over those
    ############################################################################
    with open(outfile, "w") as f:
        f.write(sep.join(varnames) + "\n")


    for id in ids:
        agent = random.choice(agents)
        headers = {'user-agent': agent}
        site = base_url + str(id)

        try:
            response = requests.get(site, headers=headers)
        except requests.exceptions.RequestException:
            wait = random.uniform(10, 15)
            sleep(wait)
            continue

        soup = BeautifulSoup(response.text, 'html.parser')

        tr_tags = soup.find_all('tr')

        outstr = ''

        for re_string in re_strings:
            varstr = ''
            for tag in tr_tags:
                pattern = re.compile(re_string)
                mname = re.search(pattern, tag.prettify())

                if mname:
                    varstr = str(mname.groups(0))
                    newline_match = re.search(re.compile(r"\\n"), varstr)
                    varstr = varstr[2:newline_match.start(0)]

            outstr = outstr + varstr + sep

        with open(outfile, "a") as f:
            f.write(outstr[:-1] + "\n")

        wait = random.uniform(1, 2)
        sleep(wait)

scraper(base_url, agents)
