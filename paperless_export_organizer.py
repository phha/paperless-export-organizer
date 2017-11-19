#!/usr/bin/env python

# Copyright (c) 2017, Philipp Hack
# All rights reserved.

from functools import partial
from datetime import datetime
from os import makedirs, symlink, path
from os.path import relpath, dirname
from json import load
import click

def link_document(relative, title, source, output_dir, subdir=""):
    """Create a symlink, including directories if necessary, or fail silently"""
    link_name = '{}.pdf'.format(path.join(output_dir, subdir, title))
    try:
        makedirs(dirname(link_name))
    except OSError:
        pass
    if relative:
        source = relpath(source, start=dirname(link_name))
    try:
        symlink(source, link_name)
    except OSError:
        pass
    return link_name



@click.command()
@click.argument('input_dir',
                type=click.Path(
                    exists=True, dir_okay=True,
                    file_okay=False, readable=True,
                    resolve_path=True))
@click.argument('output_dir',
                type=click.Path(
                    exists=False, dir_okay=True,
                    file_okay=False, readable=False,
                    writable=True, resolve_path=True))
@click.option('--relative/--no-relative', default=True,
              help='Create relative links.')
def paperless_export_organizer(input_dir, output_dir, relative):
    """Creates a directory structure with symlinks to a set of documents exported from paperless."""
    with click.open_file(path.join(input_dir, "manifest.json"), 'r') as manifest_file:
        manifest = load(manifest_file)
        tags = {}
        correspondents = {}
        documents = []
        for element in manifest:
            # Extract all tags
            if element['model'] == 'documents.tag':
                tags[element['pk']] = element['fields']
            # Extract all correspondents
            elif element['model'] == 'documents.correspondent':
                correspondents[element['pk']] = element['fields']
            # Extract all documents
            elif element['model'] == 'documents.document':
                doc = element['fields']
                try:
                    doc['created'] = datetime.strptime(doc['created'],
                        '%Y-%m-%dT%H:%M:%SZ')
                except ValueError:
                    doc['created'] = datetime.strptime(doc['created'],
                        '%Y-%m-%dT%H:%M:%S.%fZ')
                doc['filename'] = path.join(input_dir, element['__exported_file_name__'])
                documents.append(doc)

        for doc in documents:
            # Flatten tags
            doc['tags'] = [tags[t]['name'] for t in doc['tags']]
            # Resolve correspondent
            doc['correspondent'] = correspondents[doc['correspondent']]['name']
            doc['title'] = "{} - {} - {}".format(
                doc['created'].date().isoformat(), doc['correspondent'], doc['title'])
            mklink = partial(link_document, relative, doc['title'], doc['filename'], output_dir)
            mklink('all')
            mklink(path.join('by date', str(doc['created'].year), 'all'))
            mklink(path.join('by date', str(doc['created'].year),
                             str(doc['created'].strftime('%m'))))
            mklink(path.join('by correspondent', doc['correspondent'], 'all'))
            for tag in doc['tags']:
                mklink(path.join('by correspondent', doc['correspondent'], 'by tag/', tag))
                mklink(path.join('by tag/', tag, 'all'))
                mklink(path.join('by tag/', tag, 'by correspondent', doc['correspondent']))


if __name__ == '__main__':
    paperless_export_organizer()
