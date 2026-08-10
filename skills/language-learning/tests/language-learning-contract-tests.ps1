param([string]$SkillRoot = '')

$ErrorActionPreference = 'Stop'
if ([string]::IsNullOrWhiteSpace($SkillRoot)) { $SkillRoot = Split-Path -Parent $PSScriptRoot }
$SkillRoot = (Resolve-Path -LiteralPath $SkillRoot).Path
$script:failures = [System.Collections.Generic.List[string]]::new()
$script:assertions = 0

function Assert-LanguageLearning {
    param([bool]$Condition, [string]$Name)
    $script:assertions++
    if (-not $Condition) { $script:failures.Add($Name) }
}

# Match a literal phrase while tolerating line wraps (space -> any whitespace).
function Test-Phrase {
    param([string]$Text, [string]$Phrase)
    $pattern = (($Phrase -split ' ') | ForEach-Object { [regex]::Escape($_) }) -join '\s+'
    return $Text -match $pattern
}

function Test-ContextReuse {
    param([string]$Text)
    return (Test-Phrase $Text 'Reuse information already known from the current conversation') -and
           (Test-Phrase $Text 'default to beginner') -and
           (Test-Phrase $Text 'infer it only when obvious from the conversation')
}

function Test-SelectiveCorrection {
    param([string]$Text)
    return (Test-Phrase $Text 'Do not correct every mistake') -and
           (Test-Phrase $Text 'Do not enumerate every mistake') -and
           (Test-Phrase $Text 'fell off the mountain')
}

$skill = Get-Content -LiteralPath (Join-Path $SkillRoot 'SKILL.md') -Raw
$metadata = Get-Content -LiteralPath (Join-Path $SkillRoot 'agents/openai.yaml') -Raw
$refDir = Join-Path $SkillRoot 'references'
$conversation = Get-Content -LiteralPath (Join-Path $refDir 'CONVERSATION.md') -Raw
$lesson = Get-Content -LiteralPath (Join-Path $refDir 'DAILY-LESSON.md') -Raw
$flashcards = Get-Content -LiteralPath (Join-Path $refDir 'FLASHCARDS.md') -Raw
$grammar = Get-Content -LiteralPath (Join-Path $refDir 'GRAMMAR-DECODER.md') -Raw
$evaluator = Get-Content -LiteralPath (Join-Path $refDir 'PROGRESS-EVALUATOR.md') -Raw
$immersion = Get-Content -LiteralPath (Join-Path $refDir 'IMMERSION.md') -Raw

Assert-LanguageLearning ($skill -match '(?m)^name:\s*language-learning\s*$') 'frontmatter name is language-learning'
Assert-LanguageLearning ($skill -match '(?m)^disable-model-invocation:\s*true\s*$') 'Claude metadata disables model invocation'
Assert-LanguageLearning ($skill -match '(?ms)^description:.*') 'frontmatter has a description'
Assert-LanguageLearning (Test-ContextReuse $skill) 'Start section reuses context and defaults instead of re-asking'
Assert-LanguageLearning (Test-Phrase $skill 'Keep the learner producing the language') 'Teaching Behavior keeps the learner producing'
Assert-LanguageLearning (Test-Phrase $skill 'Reuse useful vocabulary, phrases, and corrections from earlier in the session') 'Teaching Behavior reuses session vocabulary and corrections'
Assert-LanguageLearning (Test-Phrase $skill 'unnecessary meta commentary') 'Teaching Behavior forbids meta commentary'
Assert-LanguageLearning (Test-Phrase $skill 'Retrieval before reveal') 'Conventions preserve retrieval before reveal'
Assert-LanguageLearning ($metadata -match 'display_name:\s*"Language Learning"') 'metadata has display name'
Assert-LanguageLearning ($metadata -match 'short_description:\s*"[^"]{25,64}"') 'metadata has bounded short description'
Assert-LanguageLearning (Test-Phrase $metadata 'Use $language-learning to get a lesson') 'metadata default prompt invokes language-learning explicitly'
Assert-LanguageLearning ($metadata -match 'allow_implicit_invocation:\s*false') 'Codex metadata disables implicit invocation'

$refs = @('DAILY-LESSON.md', 'FLASHCARDS.md', 'CONVERSATION.md', 'GRAMMAR-DECODER.md', 'PROGRESS-EVALUATOR.md', 'IMMERSION.md')
foreach ($ref in $refs) {
    Assert-LanguageLearning (Test-Path -LiteralPath (Join-Path $refDir $ref) -PathType Leaf) "references/$ref exists"
}

Assert-LanguageLearning (Test-SelectiveCorrection $conversation) 'Conversation mode corrects selectively without enumerating every mistake'
Assert-LanguageLearning (Test-Phrase $conversation 'Prioritize mistakes that affect meaning, naturalness') 'Conversation mode prioritizes meaning-affecting mistakes'
Assert-LanguageLearning (Test-Phrase $lesson 'Use the 10/10/5/5 split as a guideline rather than a rigid requirement') 'Daily lesson treats time split as a guideline'
Assert-LanguageLearning ((Test-Phrase $lesson 'explanation') -and (Test-Phrase $lesson 'exercises') -and (Test-Phrase $lesson 'quiz')) 'Daily lesson still covers explanation, examples, exercises, quiz'
Assert-LanguageLearning (Test-Phrase $flashcards 'most common everyday meaning first') 'Flashcards lead with the everyday meaning'
Assert-LanguageLearning (Test-Phrase $flashcards 'stress or IPA only when pronunciation is non-obvious') 'Flashcards gate English IPA behind non-obvious pronunciation'
Assert-LanguageLearning (Test-Phrase $grammar 'closest form learners commonly confuse') 'Grammar Decoder offers confusable contrasts when useful'
Assert-LanguageLearning ((Test-Phrase $grammar 'be used to') -and (Test-Phrase $grammar 'used to + verb')) 'Grammar Decoder shows the used to / be used to contrast'
Assert-LanguageLearning (Test-Phrase $evaluator 'concise evaluation') 'Progress Evaluator gives a concise evaluation after question 10'
Assert-LanguageLearning (Test-Phrase $evaluator 'highest-priority areas to practice next') 'Progress Evaluator names next practice priorities'
Assert-LanguageLearning (Test-Phrase $immersion 'Adapt or translate') 'Immersion Engine adapts content, not just translates'
Assert-LanguageLearning (Test-Phrase $immersion 'Stay in the target language as much as the learner can reasonably handle') 'Immersion Engine keeps the follow-up in the target language'
Assert-LanguageLearning ((Test-Phrase $immersion 'Beginner') -and (Test-Phrase $immersion 'Intermediate') -and (Test-Phrase $immersion 'Advanced')) 'Immersion Engine scales native-language support by level'

# Negative fixtures: mutating the contract in either direction must be caught.
Assert-LanguageLearning (-not (Test-ContextReuse ($skill -replace '(?is)Reuse information already known from the current conversation', 'Ask the learner to restate everything'))) 'opposite-polarity context-reuse mutation is rejected'
$overCorrect = $conversation.Replace('Do not correct every mistake.', 'Correct every mistake you hear.')
Assert-LanguageLearning (-not (Test-SelectiveCorrection $overCorrect)) 'opposite-polarity selective-correction mutation is rejected'

if ($script:assertions -eq 0) {
    throw 'LANGUAGE_LEARNING_CONTRACT=FAIL (zero assertions)'
}

if ($script:failures.Count -gt 0) {
    $script:failures | ForEach-Object { "FAIL: $_" }
    throw "LANGUAGE_LEARNING_CONTRACT=FAIL ($($script:failures.Count) failures, $script:assertions assertions)"
}

"LANGUAGE_LEARNING_CONTRACT_ASSERTIONS=$script:assertions"
"LANGUAGE_LEARNING_CONTRACT=PASS"
