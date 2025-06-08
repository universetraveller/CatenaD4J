path_to_bug_ids=""
if [ $1 ] ; then
        path_to_bug_ids=$1
fi
python3 check_out_projects.py $path_to_bug_ids /tmp/
python3 export_metadata.py $path_to_bug_ids /tmp/
