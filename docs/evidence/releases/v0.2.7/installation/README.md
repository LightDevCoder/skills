# Actual installation evidence

Successful hosted run37492680408 used main verifiera7fd7d6 against tagv0.2.7/ef2d840 and defaultmain/a7fd7d6. result.json records source and actual complete installed manifests; commands.json records exactargv/cwd/exits; parent-check.json binds their identities/digests. Independent reconstruction is recorded in ../release-evidence-evaluation.md.

command-logs.zip preserves every raw successful command log at its original name and the first failed run under first-failure/. No log bytes are changed; parent-check.json includes the successful rawfile SHA256 values. first-failure/commands.json and its archivedfailure.log preserve the wrong-root failure. Raw logs are archived because terminal output includes extra EOF blanklines; this retains exact observations while repository whitespace checks remain meaningful.

All targets are fresh hosted Linux user's real destinations, not the maintainer's global Skills. The artifact contains installation proof, not Linux/Claude runtime proof.
