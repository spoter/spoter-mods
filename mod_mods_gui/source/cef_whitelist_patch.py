# -*- coding: utf-8 -*-
"""CEF whitelist patch for the mods_gui settings page.

Why: the client refuses to load URLs that are not on its in-game browser
whitelist and answers HTTP 418 for them, so http://localhost:31338/ cannot be
displayed inside the game (see docs/t16-browser-418.md). The whitelist state is
computed in win64/cef_browser_process.exe with this instruction sequence, which
is present exactly once in both clients (EU 2.4.1 and Lesta 1.45):

    45 32 F6 EB 03 41 B6 01      xor r14b, r14b ; jmp +3 ; mov r14b, 1

The patch tools match the 7-byte stem ``45 32 F6 EB 03 41 B6`` (it is unique in
both images) and look at the following byte, so a patched image is recognised
as "already patched" instead of "signature not found".

Zeroing the last byte (the imm8 of ``mov r14b, 1``) keeps that flag at zero,
which is exactly the single byte the owner used to change manually with WinDbg.
This module performs that change explicitly, with a backup and a one-command
revert; nothing happens without an explicit ``--apply``.

Usage (run with the client's Python 2.7, or any Python 2.7):

    python cef_whitelist_patch.py --client eu                 # dry run (default)
    python cef_whitelist_patch.py --client eu --apply         # patch + verify
    python cef_whitelist_patch.py --client eu --revert        # restore backup

Only ``<client>/win64/cef_browser_process.exe`` is ever written. The backup and
its ``.json`` sidecar live outside the client tree (default: the temp dir) and
record the original sha256, so ``--revert`` can restore and verify the file.
"""

import argparse
import datetime
import hashlib
import json
import os
import shutil
import sys

SIGNATURE_STEM = '\x45\x32\xF6\xEB\x03\x41\xB6'
SIGNATURE_FULL = '\x45\x32\xF6\xEB\x03\x41\xB6\x01'
SIGNATURE_IMM_OFFSET = 7
LEGACY_GUARD = '\x41\xC6\x86\xE9\x01\x00\x00\x00\x40\x32\xF6\xEB\x03\x40\xB6\x01'
LEGACY_FALLBACK = '\x40\x32\xF6\xEB\x03\x40\xB6'
TARGET_RELATIVE = os.path.join('win64', 'cef_browser_process.exe')
CLIENTS = {
    'eu': os.path.join('D:', os.sep, 'Games', 'World_of_Tanks_EU'),
    'lesta': os.path.join('D:', os.sep, 'Games', 'Tanki_RU'),
}
DEFAULT_BACKUP_DIR = os.path.join(os.environ.get('TEMP', os.getcwd()),
                                  'mods_gui-cef-backup')


def sha256_of(path):
    """Return the sha256 hex digest of a file."""
    digest = hashlib.sha256()
    with open(path, 'rb') as handle:
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def find_all(data, needle):
    """Return every offset of ``needle`` in ``data``."""
    offsets = []
    index = data.find(needle)
    while index != -1:
        offsets.append(index)
        index = data.find(needle, index + 1)
    return offsets


def analyze(data):
    """Describe what a patch would change in this image (no writing)."""
    stem_offsets = find_all(data, SIGNATURE_STEM)
    result = {
        'size': len(data),
        'stem_offsets': stem_offsets,
        'unpatched_offsets': find_all(data, SIGNATURE_FULL),
        'legacy_guard_offsets': find_all(data, LEGACY_GUARD),
        'legacy_fallback_offsets': find_all(data, LEGACY_FALLBACK),
        'targets': [],
    }
    for offset in stem_offsets:
        position = offset + SIGNATURE_IMM_OFFSET
        if position < len(data):
            result['targets'].append({'offset': position, 'value': ord(data[position])})
    return result


def format_offsets(offsets):
    return ', '.join('0x%X' % offset for offset in offsets) or 'none'


def describe(report, verbose=False):
    """Human readable analysis report (the counts and offsets are the contract)."""
    lines = []
    lines.append('image size            : %d bytes' % report['size'])
    lines.append('signature stem (7 B)  : %d match(es) at %s'
                 % (len(report['stem_offsets']), format_offsets(report['stem_offsets'])))
    if verbose:
        lines.append('unpatched full (8 B)  : %d match(es) at %s'
                     % (len(report['unpatched_offsets']), format_offsets(report['unpatched_offsets'])))
        lines.append('legacy guard (16 B)   : %d match(es) at %s'
                     % (len(report['legacy_guard_offsets']), format_offsets(report['legacy_guard_offsets'])))
        lines.append('legacy fallback (7 B) : %d match(es) at %s'
                     % (len(report['legacy_fallback_offsets']), format_offsets(report['legacy_fallback_offsets'])))
    for target in report['targets']:
        state = 'already patched (0x00)' if target['value'] == 0 else 'would become 0x00'
        lines.append('whitelist imm8 at 0x%X : 0x%02X -> %s'
                     % (target['offset'], target['value'], state))
    return lines


def backup_paths(exe_path, backup_dir, digest):
    """Backup file plus json sidecar describing the original image."""
    name = '%s-%s' % (os.path.basename(exe_path), digest[:12])
    return (os.path.join(backup_dir, name + '.bak'),
            os.path.join(backup_dir, name + '.json'))


def make_backup(exe_path, backup_dir, digest):
    """Store the untouched image plus a sidecar with its provenance."""
    if not os.path.isdir(backup_dir):
        os.makedirs(backup_dir)
    backup_file, meta_file = backup_paths(exe_path, backup_dir, digest)
    shutil.copy2(exe_path, backup_file)
    meta = {
        'source': exe_path,
        'sha256': digest,
        'created': datetime.datetime.now().isoformat(),
        'tool': 'cef_whitelist_patch.py',
    }
    with open(meta_file, 'w') as handle:
        json.dump(meta, handle, indent=2, sort_keys=True)
    return backup_file, meta_file


def find_backups(exe_path, backup_dir):
    """All sidecars in the backup dir that describe ``exe_path``."""
    found = []
    if not os.path.isdir(backup_dir):
        return found
    target = os.path.abspath(exe_path).lower()
    for name in sorted(os.listdir(backup_dir)):
        if not name.endswith('.json'):
            continue
        meta_file = os.path.join(backup_dir, name)
        try:
            with open(meta_file) as handle:
                meta = json.load(handle)
        except (ValueError, IOError):
            continue
        if os.path.abspath(meta.get('source', '')).lower() == target:
            meta['_meta_file'] = meta_file
            meta['_backup_file'] = meta_file[:-len('.json')] + '.bak'
            found.append(meta)
    return found


def apply_patch(exe_path, report, log):
    """Zero the whitelist immediate; return the number of changed bytes."""
    with open(exe_path, 'rb') as handle:
        data = bytearray(handle.read())
    changed = []
    for target in report['targets']:
        position = target['offset']
        if data[position] != 0:
            data[position] = 0
            changed.append(position)
    if changed:
        try:
            with open(exe_path, 'wb') as handle:
                handle.write(data)
        except (IOError, OSError) as exc:
            log('ERROR: cannot write %s (%s)' % (exe_path, exc))
            log('hint: the game client is probably running and holds the file; '
                'close it and run the same command again')
            return None
    log('bytes changed         : %d at %s' % (len(changed), format_offsets(changed)))
    return changed


def run_patch(exe_path, apply_changes, backup_dir, log, verbose=False):
    """Analyse, optionally back up and patch, and verify the result."""
    if not os.path.isfile(exe_path):
        log('ERROR: target not found: %s' % exe_path)
        return 3
    digest_before = sha256_of(exe_path)
    log('target                : %s' % exe_path)
    log('sha256 before         : %s' % digest_before)
    with open(exe_path, 'rb') as handle:
        data = handle.read()
    report = analyze(data)
    for line in describe(report, verbose):
        log(line)
    if not report['stem_offsets']:
        log('ERROR: the whitelist signature was not found; nothing to do '
            '(this client build probably changed - re-derive it, see docs/t19-cef-whitelist-patch.md)')
        return 4
    if len(report['stem_offsets']) > 1:
        log('ERROR: the signature matched %d times; refusing to patch an ambiguous image'
            % len(report['stem_offsets']))
        return 4
    if not report['targets'] or report['targets'][0]['value'] == 0:
        log('nothing to do: the whitelist immediate is already zero (already patched)')
        return 0
    if not apply_changes:
        if verbose:
            log('dry run               : no byte written (use --apply to patch)')
        return 0
    backup_file, meta_file = make_backup(exe_path, backup_dir, digest_before)
    log('backup                : %s' % backup_file)
    log('backup sidecar        : %s' % meta_file)
    if sha256_of(backup_file) != digest_before:
        log('ERROR: the backup does not match the source image; aborting')
        return 9
    changed = apply_patch(exe_path, report, log)
    if changed is None:
        log('image left untouched; backup kept at %s' % backup_file)
        return 8
    digest_after = sha256_of(exe_path)
    log('sha256 after          : %s' % digest_after)
    with open(exe_path, 'rb') as handle:
        verify = analyze(handle.read())
    values = [target['value'] for target in verify['targets']]
    log('verification          : %d byte(s) changed; stem matches=%d, imm8 now %s'
        % (len(changed), len(verify['stem_offsets']),
           ', '.join('0x%02X' % value for value in values) or 'n/a'))
    if len(verify['stem_offsets']) != 1 or values != [0]:
        log('ERROR: post-patch verification failed')
        return 7
    log('revert one command    : python cef_whitelist_patch.py --exe "%s" --revert'
        % exe_path)
    return 0


def run_revert(exe_path, backup_dir, log):
    """Restore the newest backup for this image and verify its sha256."""
    backups = find_backups(exe_path, backup_dir)
    if not backups:
        log('ERROR: no backup for %s in %s' % (exe_path, backup_dir))
        return 5
    meta = backups[-1]
    backup_file = meta['_backup_file']
    if not os.path.isfile(backup_file):
        log('ERROR: backup file is missing: %s' % backup_file)
        return 5
    log('target                : %s' % exe_path)
    log('current sha256        : %s' % sha256_of(exe_path))
    log('restoring             : %s (original sha256 %s)' % (backup_file, meta['sha256']))
    shutil.copy2(backup_file, exe_path)
    digest = sha256_of(exe_path)
    log('sha256 after revert   : %s' % digest)
    if digest == meta['sha256']:
        log('revert verification   : OK (matches the pre-patch image)')
        return 0
    log('revert verification   : MISMATCH (expected %s)' % meta['sha256'])
    return 6


def main(argv=None):
    parser = argparse.ArgumentParser(description='Patch the client CEF whitelist flag '
                                                 'so the in-game browser can load http://localhost:31338/.')
    parser.add_argument('--client', choices=sorted(CLIENTS), help='client to patch')
    parser.add_argument('--exe', help='explicit path to win64/cef_browser_process.exe')
    parser.add_argument('--backup-dir', default=DEFAULT_BACKUP_DIR,
                        help='where to keep the backup (default: %s)' % DEFAULT_BACKUP_DIR)
    parser.add_argument('--apply', action='store_true',
                        help='actually write the byte (default is a dry run)')
    parser.add_argument('--revert', action='store_true', help='restore the newest backup')
    parser.add_argument('--log', help='also append the output to this file')
    parser.add_argument('--verbose', action='store_true',
                        help='also print the legacy pattern counts and the dry-run note')
    args = parser.parse_args(argv)

    if not args.exe and not args.client:
        parser.error('specify --client eu|lesta or --exe <path>')
    exe_path = args.exe or os.path.join(CLIENTS[args.client], TARGET_RELATIVE)
    log_lines = []

    def log(message):
        print(message)
        log_lines.append(message)

    log('=== cef_whitelist_patch %s ===' % datetime.datetime.now().isoformat())
    if args.revert:
        result = run_revert(exe_path, args.backup_dir, log)
    else:
        result = run_patch(exe_path, args.apply, args.backup_dir, log, args.verbose)
    if args.verbose:
        log('mode                  : %s' % ('revert' if args.revert else ('apply' if args.apply else 'dry run')))
    if args.log:
        with open(args.log, 'a') as handle:
            handle.write('\n'.join(log_lines) + '\n')
    return result


if __name__ == '__main__':
    sys.exit(main())
