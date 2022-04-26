import re
from typing import List

from telegraph import Telegraph

from services.core.utils import generator

telegraph = Telegraph(access_token='ca91370fafd7f609f048467cfc053b0577f0b7f9e9eb8890a878787390e3')


class TelegraphPlugin:

    @staticmethod
    async def add_firm_footer(html: str, last_pages: List[str] = None):
        if last_pages:
            html += '<hr>'
            html += '<img src="https://psv4.userapi.com/c856528/u106966833/docs/d12/6672113a98ef/' \
                    'Screenshot_from_2020-09-02_20-19-45.png?' \
                    'extra=KTTxYmpHYaEIo4ZIY5oARhm1U7Z04OBbx7UBeWwzdFiPduS7C4yBCP_' \
                    'iepLez3McRTJCG3ExF0f9RzYaMNDNRf_qXBFYCO4hnahlNF9ibhUaL2iewxkrDbL2ppZq1ML' \
                    '-wAyp2lhUZDqN51tbv5Dcup50Ow">'
            html += '<hr><ul>'

            async for title, url in generator(last_pages):
                html += f'<li><a href="{url}"><b>{title}</b></a></li>'

            html += '</ul><hr>'
            html += '<img src="https://psv4.userapi.com/c856224/u106966833/docs/d2/c0b0178c8330/' \
                    'Screenshot_from_2020-09-02_20-20-24.png?' \
                    'extra=lAuBGzOiJ8804LHyB0UaX2UN6zpalxeA30VmBuke8kYLFKBw1fn0VIRyAvKiXkanARQ9JGYwxri0GI' \
                    'InUfPOex7hedbrOYaIEOLXtXYwlwA5dAtG78HY6cjDmidxpCL_rW0meYhXwhg3AfleZjqD8oYTgw">'
            html += '<aside><p><a href="https://t.me/senior_software_engineer">Subscribe now!</a></p></aside>'

        return html

    @staticmethod
    async def create_page(title: str, html: str, last_pages: List[str] = None) -> str:
        html = await TelegraphPlugin.add_firm_footer(html, last_pages)
        response = telegraph.create_page(
            title,
            html_content=html
        )

        return f'https://telegra.ph/{response["path"]}'
