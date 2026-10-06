# Release workflow closeout guard acceptance

Source/package verdict: PASS; operational deployment and exact main CI follow this record, not supplied by it. project-review Core accepts C1-C6 after a fresh read-only Critic and a distinct fresh Evaluator. C7 deployment remains a subsequent action. No new tag/release or notification-policy change.

- Evaluated source29202f19cbc833ba0479198aacfe57c6aa6f42d7; baselineb687e6e10318edb013653a7072418797100565e9.
- Profileagent-skill; independencefull (Core and normalized profile); Critic2/3checks, RC001medium independentlyfixed, no otherfindings.
- Evaluator /root/release_closeout_evaluator read completepackage/diff, actualtestlogs, installedhashes/rawRPC, behaviorAgentraw7-caseJSON and readprovenance. It recommends package/sourceacceptance, explicitlykeeps deploymentpending.

| Criterion | Evidence and limit |
| --- | --- |
| C1 finalized/staged artifact links | Existing checker on actual628acd5 snapshot failsbadreceiptlinks and passesactualarchivepaths. Samebadreceiptbytes passworkspacewithuntrackedtarget and failcleanGitexport. Finalmethod exportsVERIFIED_TREE beforecheckinglinks, thenbindscommitTree. Actualtree88782f118d8ac7b46d44012bccc24e0a4770a00f exportcheckpassed. |
| C2 exactCI | Requiredcollection-quality filter, matchingheadSha, completed/success atcandidateandfinalattestation. Anyother/unreadableresult holdsstage. |
| C3 failure/repair reporting | Everyrepair repeatsfinalartifactandexactCIchecks. PreservefailureIDs/causes/fixes/current-success, distinguishfilelastmodificationbadgefromcurrentmain. |
| C4 boundary | Sixstages, receipt-afterpublication, immutabletag, authorization, metadata/invocation and36-packagecount retained; oldreleaseartifacts unchanged. |
| C5 minimalmaintenance | Matureentrychanges onlyfinalverification/CI/report gates, detailbehindreachableCLOSEOUT reference. Current bilingualMAINTENANCE correctedtoalready-publishedv027; Unreleased changes synchronized. |
| C6 install/invocation/behavior | Fresh4-fileinstalledcopyexacthashes; nativeinitialize/skills-list reportsenabledprojectpath/reposcope, withnormalexistinguserscopecopyseparately. Independentread-onlymodelagent actuallyreadinstalledSKILL/CLOSEOUT and interpreted7fixtures; correctcompletionflags andnextactions, noexternalactuation. |
| C7 deployment | User-requestedactivepackageupdate willbackup/replaceonlyrelease-workflow andverifyotherpackagesunchanged. ExactpushedmainCI and deploymentcompletion recordedlocally/inthefinaltaskreportaftertheyactuallyoccur. |

Full initialchecks:544pytest/168unittest, compile/docs/diff. Afterindexed-linkrepair,18focusedchecks andfinalexportlinkcheckpass. Finalstagedwholechecks beforepushareseparateoperational evidence.

The behavioral fixture cases are changed artifacts, wrong commit, historical red badge, unreadable CI, complete green closeout, non-release request, and untracked target. False completion is rejected in every unsafe/inapplicable case; old badge with actual passing currentCI is explained without history manipulation. This is bounded model interpretation, not execution of a realrelease. NativeCLI modelprobe failedworkspace-routingdiscovery beforecases; itsfailure ispreserved, notcountedasPASS. ActualnativeSkill discoveryisvalidseparateevidence. No executableproductresource/sharedtest change; softwareaxisN/A.

Review/rawlocal evidence under .project-review/release-closeout-20261007 and .scratch/release-closeout-20261007; acceptance sourcebriefC1-C7. Final exactCI cannotbe self-inserted into itsowncommit withoutcreatinganothercommit; closeoutbinds it externally.
