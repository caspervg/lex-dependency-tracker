import re
from urllib.parse import urlparse, parse_qs
from bs4 import BeautifulSoup, SoupStrainer
import click
from pylex import LexApi


@click.command()
@click.option('--username', prompt=True)
@click.option('--password', prompt=True, hide_input=True)
@click.option('--max', default=1)
@click.option('--dry', is_flag=True)
@click.option('--prompt-empty', is_flag=True)
@click.option('--start', default=0)
def run(username, password, max, dry, start, prompt_empty):
    api = LexApi((username, password))

    done = 0
    while done < max:
        lots = api.search_route().search(start=start,
                                         amount=20,
                                         order='desc',
                                         user=False,
                                         comments=False,
                                         votes=False,
                                         dependencies=True,
                                         filters={
                                             'order_by': 'recent',
                                             'nostrip': 'true'
                                         })

        for lot in lots:
            if lot['dependencies']['list'] is None:
                internal = []
                external = []
                click.echo("Working on lot {0} ({1})".format(lot['name'], lot['id']))

                for link in BeautifulSoup(lot['description'], "lxml", parse_only=SoupStrainer('a')):
                    if link.has_attr('href'):
                        url = link['href']
                        name = re.sub(r'\s+', ' ', link.get_text())
                        if 'csxlex/lex_filedesc' in url:
                            purl = urlparse(url)
                            lotid = parse_qs(purl[4])['lotGET'][0]
                            internal.append(lotid)
                            click.echo("Added internal ({0})".format(lotid))
                        else:
                            add = click.prompt("Found {0} with name {1}. Should it be added?".format(url, name),
                                               default=False)

                            if (not add) or add.upper() == 'F' or add.upper() == 'FALSE':
                                pass
                            elif add.upper() == 'T' or add.upper() == 'TRUE':
                                external.append((name, url))
                                click.echo("Added basic external ({0}, {1})".format(name, url))
                            elif re.match("^\d+$", add):
                                internal.append(add)
                                click.echo("Added new id internal ({0}, {1})".format(name, add))
                            elif isinstance(add, str):
                                external.append((name, add))
                                click.echo("Added new url external ({0}, {1})".format(name, add))

                add = False
                if 'no dependencies' in lot['description'].lower() and len(internal) < 1 and len(external) < 1:
                    add = click.prompt("{0} ({1}) has 'no dependencies'. Accept?".format(lot['name'], lot['id']),
                                       default=False)

                    if add:
                        add_or_dry(api, dry, lot['id'], internal, external)
                        click.echo("Added NO dependencies for {0} ({1})".format(lot['name'], lot['id']))
                if len(internal) < 1 and len(external) < 1:
                    if prompt_empty:
                        add = click.prompt("Found no dependency links for {0} ({1}). Accept as NONE?"
                                           .format(lot['name'], lot['id']), default=False)
                        if add:
                            add_or_dry(api, dry, lot['id'], internal, external)
                            click.echo("Added NO dependencies for {0} ({1})".format(lot['name'], lot['id']))
                else:
                    add = True
                    add_or_dry(api, dry, lot['id'], internal, external)
                    click.echo("Added {0} and {1} as dependencies for {2} ({3})"
                               .format(internal, external, lot['name'], lot['id']))

                if add:
                    done += 1
                if done >= max:
                    break

        start += 20


def add_or_dry(api, dry, id, internal, external):
    if not dry:
        api.lot_route().set_dependencies(id, internal, external)

if __name__ == '__main__':
    run()