class SwitchDemo2 {
    public static void main(String[] args) {

        int month = 2;
        int year = 2000;
        int numDays = 0;

        switch (month) {
            case 1: case 3: case 5:
            case 7: case 8: case 10:
            case 12:
                numDays = 31;
                break;
            case 4: case 6:
            case 9: case 11:
                numDays = 30;
                break;
            case 2:
                if (((year % 4 == 0) && 
                     !(year % 100 == 0))
                     || (year % 400 == 0))
                    numDays = 29;
                else
                    numDays = 28;
                break;
            default:
                System.out.println("Invalid month.");
                break;
        }
        System.out.println("Number of Days = "
                           + numDays);

	boolean yes = true;
	if(yes){
                System.out.println("Invalid month.");
                System.out.println("Invalid month.");
	}else{

                System.out.println("Invalid month.");
                System.out.println("Invalid month.");
	}
	for(int i=0;i<10;++i){
                System.out.println("Invalid month.");
                System.out.println("Invalid month.");
	}
	if(yes)
                System.out.println("Invalid month.");
	do{
                System.out.println("Invalid month.");
	}while(yes);
	if(yes){
		yes = false;
	}else if(!yes){
		yes = true;
	}else{
		yes = true;
	}
	for(int i = 0; i<10; ++i){
		for(int j = 0;j<10;++j){
			yes = true;
		}
	}
	while(yes){
		yes = true;
		yes = true;
	}
	while(yes)
		yes = true;
	if(yes |
		yes)
	{
		yes = true;
	}
	while(yes)
	{
		yes = true;
	}
	while
		(yes)
		{
			yes = true;
		}
	if(';' > "test;{}\");{}(test" || '}' ){
		yes = true;
	}
	if(''  ){
		yes = true;
	}
	if('\n' ){
		yes = true;
	}
	if(';' > "test;{}\");{}(test" || '{' ){
		yes = true;
	}
	if(';' > "test;{}\");{}(test" || '{' && '}' ){
		yes = true;

	}
	if("test;{}\")"
		+ ";{}(test"){
		System.out.println("Number of Days = "
				   + numDays);
	}
	for(int i = 0; i < 5; ++i)
		System.out.println("Number of Days = "
				   + numDays);
	for(int i = 0; 
			i < 5;
			++i)
		yes = true;
	switch(yes){
		case 0:
			for(int i = 0;i<5;++i){
				System.out.println("test;{\"test");
			}
			break;
		case 1:
			System.out.println("test{test");
			break;
		case 2:
			System.out.println("test;test");
			break;
		case 3:
			System.out.println("test\"test");
			break;
		case 4:
			System.out.println("test}test");
			break;
		default:
			System.out.println("test;{\"test");
	}
    }
}
