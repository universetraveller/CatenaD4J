if ! command -v pip &> /dev/null
then
	apt-get update -y
	apt-get install -y pip
fi
pip install joblib
pip install tqdm
