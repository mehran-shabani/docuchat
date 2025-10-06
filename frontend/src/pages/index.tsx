export default function Home() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100" dir="rtl">
      <div className="text-center p-8 bg-white rounded-2xl shadow-xl">
        <h1 className="text-4xl font-bold text-indigo-600 mb-4">
          DocuChat
        </h1>
        <p className="text-xl text-gray-700">
          DocuChat is live
        </p>
        <p className="text-sm text-gray-500 mt-4">
          نسخه 0.1.0
        </p>
      </div>
    </div>
  );
}
