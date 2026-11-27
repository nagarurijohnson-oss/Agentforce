set -u
O=orgfarm-232477b490-dev-ed; B=Contact_Read_Agent; D=../casetest2
run_session () {
  tag=$1; shift
  sid=$(sf agent preview start --authoring-bundle $B --use-live-actions --target-org $O --json 2>$D/$tag-start.err | python3 -c "import json,sys;d=json.load(sys.stdin);print(d['result'].get('sessionId',''))")
  echo "$tag session $sid"; echo $sid > $D/$tag-sid.txt
  i=0
  for u in "$@"; do i=$((i+1))
    sf agent preview send --authoring-bundle $B --session-id "$sid" --utterance "$u" --target-org $O --json 2>>$D/$tag-send.err > $D/$tag-turn$i.json
    echo "--- [$tag $i] $u"
    python3 -c "import json;d=json.load(open('$D/$tag-turn$i.json'));r=d.get('result',d);print('\n'.join(m.get('message','') for m in r.get('messages',[]))[:900] or json.dumps(d)[:600])"
  done
  sf agent trace read -s "$sid" -f summary --json > $D/$tag-trace.json 2>$D/$tag-trace.err
  sf agent trace read -s "$sid" -f detail -d actions --json > $D/$tag-trace-actions.json 2>>$D/$tag-trace.err
  sf agent trace read -s "$sid" -f detail -d errors --json > $D/$tag-trace-errors.json 2>>$D/$tag-trace.err
  sf agent preview end --authoring-bundle $B --session-id "$sid" --target-org $O --json > $D/$tag-end.json 2>&1
}
"$@"
