public class java{
	private static test(){
		this.test();
    Method tester = new Method() {
      @Override
      public boolean call(NodeTraversal t, Node n, Node parent) {
        CanInlineResult result = injector.canInlineReferenceToFunction(
            t, n, fnNode, unsafe, mode,
            NodeUtil.referencesThis(fnNode),
            NodeUtil.containsFunction(NodeUtil.getFunctionBody(fnNode)));
        assertEquals(expectedResult, result);
        return true;
      }
    };
		di1(test);
	}
}
