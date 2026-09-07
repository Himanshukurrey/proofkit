Output demo/proofkit-demo.gif

Set Shell "zsh"
Set FontSize 18
Set Width 1100
Set Height 650
Set Padding 20
Set TypingSpeed 45ms
Set Theme "Dracula"

Hide
Type "export PATH=/opt/homebrew/Caskroom/miniconda/base/envs/proj_1/bin:$PATH"
Enter
Type "cd /Users/himanshu/projects/proofkit"
Enter
Type "clear"
Enter
Show

Type "proofkit capture -o bug.proof -- python demo/top_n_buggy.py 5 3 9 1 7 5"
Enter
Sleep 2s

Type "proofkit verify bug.proof"
Enter
Sleep 2500ms

Type "echo '--- an AI agent applies a fix and commits it ---'"
Enter
Sleep 500ms
Type "sed -i '' 's/sorted_items\[n\]/sorted_items[:n]/' demo/top_n_buggy.py"
Enter
Sleep 500ms
Type "git commit -am 'Fix off-by-one: slice instead of index'"
Enter
Sleep 1500ms

Type "proofkit verify bug.proof"
Enter
Sleep 2500ms
