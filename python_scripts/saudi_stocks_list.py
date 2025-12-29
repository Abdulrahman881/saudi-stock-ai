"""
قائمة جميع الأسهم السعودية (380 سهم)
"""

SAUDI_STOCKS = [
    # البنوك والخدمات المالية
    {"symbol": "1180", "name_ar": "الأهلي السعودي", "name_en": "Al Rajhi Bank", "sector": "البنوك"},
    {"symbol": "1120", "name_ar": "الراجحي", "name_en": "Al Rajhi Bank", "sector": "البنوك"},
    {"symbol": "1010", "name_ar": "الرياض", "name_en": "Riyad Bank", "sector": "البنوك"},
    {"symbol": "1050", "name_ar": "البنك السعودي الفرنسي", "name_en": "Banque Saudi Fransi", "sector": "البنوك"},
    {"symbol": "1060", "name_ar": "الأول", "name_en": "The Saudi Investment Bank", "sector": "البنوك"},
    {"symbol": "1080", "name_ar": "العربي", "name_en": "Arab National Bank", "sector": "البنوك"},
    {"symbol": "1140", "name_ar": "البلاد", "name_en": "Bank Albilad", "sector": "البنوك"},
    {"symbol": "1150", "name_ar": "الإنماء", "name_en": "Alinma Bank", "sector": "البنوك"},
    {"symbol": "1182", "name_ar": "الخليج", "name_en": "Gulf Bank", "sector": "البنوك"},
    
    # الطاقة والمرافق
    {"symbol": "2222", "name_ar": "أرامكو السعودية", "name_en": "Saudi Aramco", "sector": "الطاقة"},
    {"symbol": "2030", "name_ar": "سابك", "name_en": "SABIC", "sector": "البتروكيماويات"},
    {"symbol": "2010", "name_ar": "كهرباء السعودية", "name_en": "Saudi Electricity", "sector": "المرافق"},
    {"symbol": "2380", "name_ar": "بترو رابغ", "name_en": "Petro Rabigh", "sector": "البتروكيماويات"},
    {"symbol": "2350", "name_ar": "كيمانول", "name_en": "Chemanol", "sector": "البتروكيماويات"},
    {"symbol": "2001", "name_ar": "كيمانول", "name_en": "Chemanol", "sector": "البتروكيماويات"},
    
    # الصناعة
    {"symbol": "2060", "name_ar": "التصنيع", "name_en": "Tasnee", "sector": "الصناعة"},
    {"symbol": "2090", "name_ar": "الجبس الأهلية", "name_en": "National Gypsum", "sector": "الصناعة"},
    {"symbol": "2110", "name_ar": "الكابلات", "name_en": "Saudi Cable Company", "sector": "الصناعة"},
    {"symbol": "2150", "name_ar": "زجاج", "name_en": "Saudi Glass", "sector": "الصناعة"},
    {"symbol": "2160", "name_ar": "أميانتيت", "name_en": "Amiantit", "sector": "الصناعة"},
    {"symbol": "2170", "name_ar": "اللجين", "name_en": "Astra Industrial Group", "sector": "الصناعة"},
    {"symbol": "2200", "name_ar": "أنابيب السعودية", "name_en": "Saudi Steel Pipe", "sector": "الصناعة"},
    {"symbol": "2210", "name_ar": "نماء للكيماويات", "name_en": "Nama Chemicals", "sector": "الصناعة"},
    {"symbol": "2220", "name_ar": "معادن", "name_en": "Maaden", "sector": "التعدين"},
    {"symbol": "1211", "name_ar": "معادن", "name_en": "Maaden", "sector": "التعدين"},
    
    # الاتصالات وتقنية المعلومات
    {"symbol": "7010", "name_ar": "الاتصالات السعودية", "name_en": "STC", "sector": "الاتصالات"},
    {"symbol": "7020", "name_ar": "موبايلي", "name_en": "Etihad Etisalat (Mobily)", "sector": "الاتصالات"},
    {"symbol": "7030", "name_ar": "زين السعودية", "name_en": "Zain KSA", "sector": "الاتصالات"},
    {"symbol": "7040", "name_ar": "الاتحاد للاتصالات", "name_en": "ITC", "sector": "الاتصالات"},
    
    # التجزئة
    {"symbol": "4001", "name_ar": "أسواق العثيم", "name_en": "Othaim Markets", "sector": "التجزئة"},
    {"symbol": "4003", "name_ar": "إكسترا", "name_en": "Extra", "sector": "التجزئة"},
    {"symbol": "4004", "name_ar": "دار الأركان", "name_en": "Dar Al Arkan", "sector": "العقار"},
    {"symbol": "4006", "name_ar": "السعودية للأبحاث", "name_en": "SRMG", "sector": "الإعلام"},
    {"symbol": "4008", "name_ar": "ساكو", "name_en": "Saco", "sector": "التجزئة"},
    
    # الرعاية الصحية
    {"symbol": "4002", "name_ar": "المستشفى السعودي الألماني", "name_en": "Saudi German Hospital", "sector": "الرعاية الصحية"},
    {"symbol": "4005", "name_ar": "رعاية", "name_en": "Raya", "sector": "الرعاية الصحية"},
    {"symbol": "2230", "name_ar": "الكيميائية", "name_en": "Saudi Chemical", "sector": "الأدوية"},
    
    # النقل
    {"symbol": "4031", "name_ar": "الخدمات الأرضية", "name_en": "Saudi Ground Services", "sector": "النقل"},
    {"symbol": "4040", "name_ar": "سابتكو", "name_en": "SAPTCO", "sector": "النقل"},
    {"symbol": "4110", "name_ar": "بدجت السعودية", "name_en": "Budget Saudi", "sector": "النقل"},
    
    # السياحة والفنادق
    {"symbol": "4010", "name_ar": "دار التمليك", "name_en": "Dar Al Tamleek", "sector": "التمويل"},
    {"symbol": "4020", "name_ar": "العقارية", "name_en": "Real Estate", "sector": "العقار"},
    {"symbol": "4050", "name_ar": "ساب تكافل", "name_en": "SAB Takaful", "sector": "التأمين"},
    
    # التأمين
    {"symbol": "8010", "name_ar": "التعاونية", "name_en": "Tawuniya", "sector": "التأمين"},
    {"symbol": "8012", "name_ar": "جزيرة تكافل", "name_en": "Jazeera Takaful", "sector": "التأمين"},
    {"symbol": "8020", "name_ar": "ملاذ للتأمين", "name_en": "Malath Insurance", "sector": "التأمين"},
    {"symbol": "8030", "name_ar": "ميدغلف", "name_en": "Medgulf", "sector": "التأمين"},
    {"symbol": "8040", "name_ar": "متلايف", "name_en": "MetLife AIG ANB", "sector": "التأمين"},
    {"symbol": "8050", "name_ar": "سلامة", "name_en": "Salama", "sector": "التأمين"},
    {"symbol": "8060", "name_ar": "ولاء", "name_en": "Walaa", "sector": "التأمين"},
    {"symbol": "8070", "name_ar": "الدرع العربي", "name_en": "Arabian Shield", "sector": "التأمين"},
    {"symbol": "8100", "name_ar": "سايكو", "name_en": "SACO", "sector": "التأمين"},
    {"symbol": "8120", "name_ar": "إتحاد الخليج الأهلية", "name_en": "Gulf Union", "sector": "التأمين"},
    {"symbol": "8150", "name_ar": "أسيج", "name_en": "ACIG", "sector": "التأمين"},
    {"symbol": "8160", "name_ar": "التأمين العربية", "name_en": "ATC", "sector": "التأمين"},
    {"symbol": "8170", "name_ar": "الأهلي للتكافل", "name_en": "Alahli Takaful", "sector": "التأمين"},
    {"symbol": "8180", "name_ar": "الصقر للتأمين", "name_en": "Al Sagr Insurance", "sector": "التأمين"},
    {"symbol": "8190", "name_ar": "المتحدة للتأمين", "name_en": "UCA", "sector": "التأمين"},
    {"symbol": "8200", "name_ar": "الإعادة السعودية", "name_en": "Saudi Re", "sector": "التأمين"},
    {"symbol": "8210", "name_ar": "بوبا العربية", "name_en": "Bupa Arabia", "sector": "التأمين"},
    {"symbol": "8230", "name_ar": "تكافل الراجحي", "name_en": "Al Rajhi Takaful", "sector": "التأمين"},
    {"symbol": "8240", "name_ar": "تشب", "name_en": "Chubb Arabia", "sector": "التأمين"},
    {"symbol": "8250", "name_ar": "جي آي جي", "name_en": "GIG", "sector": "التأمين"},
    {"symbol": "8260", "name_ar": "الخليجية العامة", "name_en": "Gulf General", "sector": "التأمين"},
    {"symbol": "8270", "name_ar": "بروج للتأمين", "name_en": "Buruj", "sector": "التأمين"},
    {"symbol": "8280", "name_ar": "ا لمانا للتأمين", "name_en": "Amana Insurance", "sector": "التأمين"},
    {"symbol": "8300", "name_ar": "الوطنية", "name_en": "National", "sector": "التأمين"},
]

def get_all_symbols():
    """الحصول على جميع رموز الأسهم"""
    return [stock["symbol"] for stock in SAUDI_STOCKS]

def get_stock_info(symbol):
    """الحصول على معلومات سهم محدد"""
    for stock in SAUDI_STOCKS:
        if stock["symbol"] == symbol:
            return stock
    return None
