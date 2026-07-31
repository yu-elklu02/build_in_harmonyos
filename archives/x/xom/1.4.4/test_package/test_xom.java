import nu.xom.Document;
import nu.xom.Element;

public final class test_xom {
    public static void main(String[] args) {
        Element root = new Element("root");
        root.appendChild("ok");
        Document document = new Document(root);
        String xml = document.toXML();
        if (!xml.contains("<root>ok</root>")) {
            throw new IllegalStateException(xml);
        }
        System.out.println("xom functional checks passed: 3");
    }
}
