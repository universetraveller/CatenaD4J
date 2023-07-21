public class test1{
	public static void main(String[] args){

		t(1);
	}
	public static void t(int a){
		try{
		a=1;
		throw new Error("1");
		}catch(Throwable __SHOULD_BE_IGNORED){}
	}
}
