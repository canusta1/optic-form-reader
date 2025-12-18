import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'upload_screen.dart';
import 'forms_screen.dart';
import 'history_screen.dart';
import 'login_screen.dart';
import 'auth_service.dart';
import 'api_config.dart';

void main() async {
  // Flutter binding'leri başlat (async main için gerekli)
  WidgetsFlutterBinding.ensureInitialized();

  // API bağlantı ayarlarını başlat (kaydedilmiş IP varsa yükler)
  await ApiConfig.initializeBaseUrl();
  ApiConfig.printConfig();
  runApp(const OpticFormApp());
}

class OpticFormApp extends StatelessWidget {
  const OpticFormApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Optik Form Okuyucu',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF2979FF), // Electric Blue
          brightness: Brightness.light,
          primary: const Color(0xFF2979FF),
          secondary: const Color(0xFF00E5FF), // Neon Cyan
          surface: const Color(0xFFF5F7FA),
        ),
        useMaterial3: true,
        textTheme: GoogleFonts.poppinsTextTheme(),
        scaffoldBackgroundColor: const Color(0xFFF5F7FA),
        appBarTheme: AppBarTheme(
          backgroundColor: Colors.transparent,
          elevation: 0,
          centerTitle: true,
          titleTextStyle: GoogleFonts.poppins(
            fontWeight: FontWeight.bold,
            fontSize: 20,
            color: const Color(0xFF1A237E),
          ),
          iconTheme: const IconThemeData(color: Color(0xFF1A237E)),
        ),
        cardTheme: CardTheme(
          elevation: 8,
          shadowColor: Colors.black.withOpacity(0.1),
          shape:
              RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        ),
        elevatedButtonTheme: ElevatedButtonThemeData(
          style: ElevatedButton.styleFrom(
            elevation: 4,
            shadowColor: const Color(0xFF2979FF).withOpacity(0.4),
            shape:
                RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
            padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 24),
            backgroundColor: const Color(0xFF2979FF),
            foregroundColor: Colors.white,
          ),
        ),
      ),
      home: AuthService.isLoggedIn ? const MainScreen() : const LoginScreen(),
    );
  }
}

class MainScreen extends StatefulWidget {
  const MainScreen({super.key});

  @override
  State<MainScreen> createState() => _MainScreenState();
}

class _MainScreenState extends State<MainScreen> {
  int _currentIndex = 0;

  final List<Widget> _screens = [
    const UploadScreen(),
    const FormsScreen(),
    const HistoryScreen(),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      extendBody: true, // BottomNavBar arkasına içerik taşsın
      appBar: AppBar(
        title: const Text('Optik Form Okuyucu'),
        flexibleSpace: Container(
          decoration: const BoxDecoration(
            gradient: LinearGradient(
              colors: [Color(0xFFF5F7FA), Color(0xFFE3F2FD)],
              begin: Alignment.topCenter,
              end: Alignment.bottomCenter,
            ),
          ),
        ),
        actions: [
          Container(
            margin: const EdgeInsets.only(right: 16),
            decoration: BoxDecoration(
              color: Colors.white,
              shape: BoxShape.circle,
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.05),
                  blurRadius: 10,
                  offset: const Offset(0, 4),
                ),
              ],
            ),
            child: IconButton(
              icon: const Icon(Icons.person_outline_rounded),
              onPressed: () {
                _showProfileMenu(context);
              },
            ),
          ),
        ],
      ),
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [Color(0xFFF5F7FA), Color(0xFFE3F2FD)],
          ),
        ),
        child: _screens[_currentIndex],
      ),
      bottomNavigationBar: Container(
        margin: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(30),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.1),
              blurRadius: 20,
              offset: const Offset(0, 10),
            ),
          ],
        ),
        child: ClipRRect(
          borderRadius: BorderRadius.circular(30),
          child: BottomNavigationBar(
            currentIndex: _currentIndex,
            onTap: (index) => setState(() => _currentIndex = index),
            backgroundColor: Colors.white,
            selectedItemColor: const Color(0xFF2979FF),
            unselectedItemColor: Colors.grey.shade400,
            showUnselectedLabels: true,
            type: BottomNavigationBarType.fixed,
            elevation: 0,
            items: const [
              BottomNavigationBarItem(
                icon: Icon(Icons.camera_alt_outlined),
                activeIcon: Icon(Icons.camera_alt_rounded),
                label: 'Analiz',
              ),
              BottomNavigationBarItem(
                icon: Icon(Icons.assignment_outlined),
                activeIcon: Icon(Icons.assignment_rounded),
                label: 'Formlarım',
              ),
              BottomNavigationBarItem(
                icon: Icon(Icons.history_outlined),
                activeIcon: Icon(Icons.history_rounded),
                label: 'Geçmiş',
              ),
            ],
          ),
        ),
      ),
    );
  }

  void _showProfileMenu(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Profil'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Hoş geldin,',
              style: TextStyle(fontSize: 14, color: Colors.grey[600]),
            ),
            const SizedBox(height: 4),
            Text(
              AuthService.currentUser?['full_name'] ??
                  AuthService.currentUser?['username'] ??
                  'Kullanıcı',
              style: const TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            if (AuthService.currentUser?['email'] != null) ...[
              const SizedBox(height: 8),
              Text(
                AuthService.currentUser!['email'],
                style: TextStyle(fontSize: 14, color: Colors.grey[600]),
              ),
            ],
          ],
        ),
        actions: [
          TextButton(
            onPressed: () {
              Navigator.of(context).pop();
            },
            child: const Text('Kapat'),
          ),
          TextButton(
            onPressed: () {
              AuthService.logout();
              Navigator.of(context).pop();
              Navigator.of(context).pushReplacement(
                MaterialPageRoute(builder: (_) => const LoginScreen()),
              );
            },
            style: TextButton.styleFrom(foregroundColor: Colors.red),
            child: const Text('Çıkış Yap'),
          ),
        ],
      ),
    );
  }
}
