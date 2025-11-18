"""
Message templates for alerts in Turkish.
Professional formatting for managers and technical details for safety officers.
"""

from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum


class TemplateType(Enum):
    """Template types for different audiences."""
    MANAGER = "manager"          # Brief, actionable
    SAFETY_OFFICER = "safety"    # Technical details
    SUPERVISOR = "supervisor"    # Operational focus
    SUMMARY = "summary"          # Daily/weekly reports


class AlertTemplates:
    """Turkish message templates for PPE violation alerts."""

    # PPE item names in Turkish
    PPE_NAMES = {
        "helmet": "Baret",
        "vest": "İkaz Yeleği",
        "gloves": "Eldiven",
        "safety_shoes": "Güvenlik Ayakkabısı",
        "goggles": "Koruyucu Gözlük",
        "mask": "Maske",
        "harness": "Emniyet Kemeri",
        "ear_protection": "Kulak Koruyucu"
    }

    # Violation severity in Turkish
    SEVERITY_NAMES = {
        "critical": "KRİTİK",
        "warning": "UYARI",
        "info": "BİLGİ"
    }

    @staticmethod
    def format_violation_alert(
        template_type: TemplateType,
        priority: str,
        zone: str,
        camera_id: str,
        missing_ppe: List[str],
        timestamp: datetime,
        worker_id: Optional[str] = None,
        image_url: Optional[str] = None,
        violation_count: int = 1,
        compliance_rate: Optional[float] = None
    ) -> str:
        """Format a PPE violation alert message."""

        if template_type == TemplateType.MANAGER:
            return AlertTemplates._format_manager_alert(
                priority, zone, missing_ppe, timestamp, violation_count, compliance_rate
            )
        elif template_type == TemplateType.SAFETY_OFFICER:
            return AlertTemplates._format_safety_officer_alert(
                priority, zone, camera_id, missing_ppe, timestamp,
                worker_id, image_url, violation_count
            )
        elif template_type == TemplateType.SUPERVISOR:
            return AlertTemplates._format_supervisor_alert(
                priority, zone, missing_ppe, timestamp, worker_id
            )
        else:
            return AlertTemplates._format_manager_alert(
                priority, zone, missing_ppe, timestamp, violation_count, compliance_rate
            )

    @staticmethod
    def _format_manager_alert(
        priority: str,
        zone: str,
        missing_ppe: List[str],
        timestamp: datetime,
        violation_count: int,
        compliance_rate: Optional[float]
    ) -> str:
        """Brief alert for managers - focus on action needed."""
        severity = AlertTemplates.SEVERITY_NAMES.get(priority.lower(), "UYARI")
        ppe_list = ", ".join([AlertTemplates.PPE_NAMES.get(ppe, ppe) for ppe in missing_ppe])

        message = f"""
🚨 {severity} - KKD İhlali Tespit Edildi

📍 Bölge: {zone}
⏰ Zaman: {timestamp.strftime('%d.%m.%Y %H:%M:%S')}
⚠️ Eksik KKD: {ppe_list}
"""

        if violation_count > 1:
            message += f"📊 Son 10 dakikada {violation_count} ihlal tespit edildi\n"

        if compliance_rate is not None:
            message += f"📈 Mevcut Uyum Oranı: %{compliance_rate * 100:.1f}\n"

        message += """
🎯 Gerekli Aksiyon:
• Bölge şefini bilgilendir
• Çalışanları uyar
• KKD kullanımını sağla
"""
        return message.strip()

    @staticmethod
    def _format_safety_officer_alert(
        priority: str,
        zone: str,
        camera_id: str,
        missing_ppe: List[str],
        timestamp: datetime,
        worker_id: Optional[str],
        image_url: Optional[str],
        violation_count: int
    ) -> str:
        """Detailed technical alert for safety officers."""
        severity = AlertTemplates.SEVERITY_NAMES.get(priority.lower(), "UYARI")
        ppe_list = ", ".join([AlertTemplates.PPE_NAMES.get(ppe, ppe) for ppe in missing_ppe])

        message = f"""
{'='*50}
İSG İHLAL RAPORU - {severity}
{'='*50}

📋 GENEL BİLGİLER:
• Olay No: VIO-{timestamp.strftime('%Y%m%d%H%M%S')}
• Tarih/Saat: {timestamp.strftime('%d.%m.%Y %H:%M:%S')}
• Bölge: {zone}
• Kamera ID: {camera_id}

👷 ÇALIŞAN BİLGİSİ:
• Çalışan Kimliği: {worker_id or 'Tespit Edilemedi'}

⚠️ İHLAL DETAYI:
• Eksik KKD: {ppe_list}
• İhlal Sayısı (Son 10 dk): {violation_count}

📸 GÖRSEL KAYIT:
"""
        if image_url:
            message += f"• Fotoğraf: {image_url}\n"
        else:
            message += "• Fotoğraf: Mevcut değil\n"

        message += """
🔍 YAPILMASI GEREKENLER:
1. Çalışanla birebir görüşme yap
2. KKD'nin temin edilip edilmediğini kontrol et
3. Gerekirse KKD dağıt
4. İhlal formunu doldur
5. Gerekirse disiplin işlemi başlat
6. Bölge şefini bilgilendir

⚖️ YASAL ÇERÇEVE:
• İSG Yönetmeliği Madde 4
• 6331 Sayılı İSG Kanunu

📞 ACİL DURUM:
• İSG Koordinatörü: int. 1234
• 112 Acil: 112
"""
        return message.strip()

    @staticmethod
    def _format_supervisor_alert(
        priority: str,
        zone: str,
        missing_ppe: List[str],
        timestamp: datetime,
        worker_id: Optional[str]
    ) -> str:
        """Practical alert for supervisors - focus on immediate action."""
        severity = AlertTemplates.SEVERITY_NAMES.get(priority.lower(), "UYARI")
        ppe_list = ", ".join([AlertTemplates.PPE_NAMES.get(ppe, ppe) for ppe in missing_ppe])

        message = f"""
⚠️ {severity} - KKD Kontrolü Gerekli

📍 Bölge: {zone}
⏰ Saat: {timestamp.strftime('%H:%M')}
👷 Çalışan: {worker_id or 'Tespit edilmedi'}

❌ Eksik KKD: {ppe_list}

✅ Hemen Yapılacaklar:
1. Bölgeye git
2. Çalışanı tespit et
3. KKD kullanımını sağla
4. Güvenliği kontrol et

Not: 5 dakika içinde aksiyon alınmazsa üst yönetime bildirilecektir.
"""
        return message.strip()

    @staticmethod
    def format_summary_report(
        period: str,
        total_violations: int,
        compliance_rate: float,
        top_violations: List[Dict],
        top_zones: List[Dict],
        trend: str,
        start_date: datetime,
        end_date: datetime
    ) -> str:
        """Format daily/weekly summary report."""

        message = f"""
{'='*60}
KKD UYUM RAPORU - {period.upper()}
{'='*60}

📅 DÖNEM: {start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}

📊 GENEL İSTATİSTİKLER:
• Toplam İhlal: {total_violations}
• Uyum Oranı: %{compliance_rate * 100:.1f}
• Trend: {trend}

⚠️ EN ÇOK GÖRÜLEN İHLALLER:
"""
        for i, violation in enumerate(top_violations[:5], 1):
            ppe_name = AlertTemplates.PPE_NAMES.get(violation['ppe'], violation['ppe'])
            message += f"{i}. {ppe_name}: {violation['count']} ihlal\n"

        message += "\n📍 EN ÇOK İHLAL OLAN BÖLGELER:\n"
        for i, zone in enumerate(top_zones[:5], 1):
            message += f"{i}. {zone['name']}: {zone['count']} ihlal\n"

        # Add recommendations based on data
        message += "\n🎯 ÖNERİLER:\n"

        if compliance_rate < 0.80:
            message += "• ❗ Uyum oranı hedefin altında! Eğitim programı düzenleyin\n"

        if top_zones and top_zones[0]['count'] > 10:
            message += f"• ⚠️ {top_zones[0]['name']} bölgesinde yoğun ihlal var - ek denetim gerekli\n"

        if trend == "Artış":
            message += "• 📈 İhlaller artış trendinde - acil müdahale gerekli\n"
        elif trend == "Azalış":
            message += "• 📉 İhlaller azalış trendinde - mevcut uygulamalar etkili\n"

        message += """
📋 DETAYLI RAPOR:
• Detaylı analiz için dashboard'u ziyaret edin
• Sorumlu: İSG Ekibi

─────────────────────────────────────────────────────
Bu rapor otomatik olarak oluşturulmuştur.
"""
        return message.strip()

    @staticmethod
    def format_escalation_alert(
        original_alert_time: datetime,
        zone: str,
        violation_type: str,
        escalation_level: int,
        time_elapsed_minutes: int
    ) -> str:
        """Format escalation alert when no action is taken."""

        message = f"""
🔴 ESKALASYON SEVİYE {escalation_level}

⚠️ Bildirilen ihlale {time_elapsed_minutes} dakikadır müdahale edilmedi!

📍 Bölge: {zone}
⏰ İlk Bildirim: {original_alert_time.strftime('%d.%m.%Y %H:%M:%S')}
❌ İhlal Türü: {violation_type}

🚨 ACİL MÜDAHALE GEREKLİ
• Bölge şefini acilen kontrol edin
• Durumu onaylayın veya çözümleyin
• Bu bildirimi onaylayın

{'─'*50}
Level {escalation_level} - Üst yönetim bilgilendirildi
"""
        return message.strip()

    @staticmethod
    def format_compliance_threshold_alert(
        zone: str,
        current_rate: float,
        threshold: float,
        period_hours: int
    ) -> str:
        """Alert when compliance rate falls below threshold."""

        message = f"""
📉 UYUM ORANI DÜŞTÜKRİTİK SEVİYE!

📍 Bölge: {zone}
📊 Mevcut Uyum: %{current_rate * 100:.1f}
⚠️ Eşik Değer: %{threshold * 100:.1f}
⏱️ Periyot: Son {period_hours} saat

🚨 DURUM: Uyum oranı kabul edilebilir seviyenin altında!

✅ ALINMASI GEREKEN AKSIYONLAR:
1. Bölgede genel KKD denetimi yapın
2. Eksik KKD'leri dağıtın
3. Çalışanlara kısa eğitim verin
4. Uyarı levhaları kontrolü yapın
5. Bölge şefi ile görüşün

📞 Destek için İSG Ekibini arayın: int. 1234
"""
        return message.strip()

    @staticmethod
    def format_critical_zone_alert(
        zone: str,
        missing_ppe: List[str],
        timestamp: datetime,
        risk_level: str = "YÜKSEK"
    ) -> str:
        """Special format for critical zone violations."""
        ppe_list = ", ".join([AlertTemplates.PPE_NAMES.get(ppe, ppe) for ppe in missing_ppe])

        message = f"""
🔴🔴🔴 KRİTİK BÖLGE İHLALİ 🔴🔴🔴

⚠️ YÜKSEKRİSK BÖLGEDE KKD İHLALİ TESPİT EDİLDİ!

📍 Bölge: {zone}
🎯 Risk Seviyesi: {risk_level}
⏰ Zaman: {timestamp.strftime('%d.%m.%Y %H:%M:%S')}
❌ Eksik KKD: {ppe_list}

🚨 ACİL MÜDAHALE ZORUNLU:
1. ÇALIŞMAYI DERHAL DURDUR
2. Çalışanı bölgeden uzaklaştır
3. KKD'yi temin et ve kullandır
4. Risk değerlendirmesi yap
5. Çalışma izni kontrol et

⚖️ YASAL SORUMLULUK:
Kritik bölgelerde KKD kullanımı ZORUNLU!
İhlaller yasal yaptırımlara tabi olabilir.

{'─'*50}
Bu mesaj tüm yetkililere gönderilmiştir.
"""
        return message.strip()

    @staticmethod
    def format_acknowledgment_request(
        alert_id: str,
        zone: str,
        timestamp: datetime
    ) -> str:
        """Request acknowledgment for alert."""

        message = f"""
✋ ONAY BEKLENİYOR

Alert ID: {alert_id}
Bölge: {zone}
Zaman: {timestamp.strftime('%d.%m.%Y %H:%M:%S')}

Lütfen durumu kontrol ettikten sonra:
• Web dashboard'dan onaylayın
• Veya 'ONAYLA {alert_id}' mesajı gönderin

Not: 1 saat içinde onaylanmazsa otomatik eskalasyon başlar.
"""
        return message.strip()

    @staticmethod
    def format_sms_alert(
        zone: str,
        missing_ppe: List[str],
        priority: str
    ) -> str:
        """Short format for SMS (160 characters limit)."""
        severity = AlertTemplates.SEVERITY_NAMES.get(priority.lower(), "UYARI")
        ppe_list = ", ".join([AlertTemplates.PPE_NAMES.get(ppe, ppe) for ppe in missing_ppe[:2]])

        if len(missing_ppe) > 2:
            ppe_list += f" +{len(missing_ppe) - 2}"

        message = f"{severity}: {zone} - Eksik: {ppe_list}. Derhal kontrol edin!"

        # Ensure it fits in SMS limit
        if len(message) > 160:
            message = message[:157] + "..."

        return message

    @staticmethod
    def format_email_subject(
        priority: str,
        zone: str,
        alert_type: str = "KKD İhlali"
    ) -> str:
        """Format email subject line."""
        severity = AlertTemplates.SEVERITY_NAMES.get(priority.lower(), "UYARI")
        return f"[{severity}] {alert_type} - {zone}"

    @staticmethod
    def format_webhook_payload(
        priority: str,
        zone: str,
        camera_id: str,
        missing_ppe: List[str],
        timestamp: datetime,
        worker_id: Optional[str] = None,
        image_url: Optional[str] = None,
        violation_count: int = 1,
        compliance_rate: Optional[float] = None
    ) -> Dict:
        """Format data for webhook integrations (Slack, Teams, etc.)."""
        return {
            "type": "ppe_violation",
            "priority": priority,
            "timestamp": timestamp.isoformat(),
            "zone": zone,
            "camera_id": camera_id,
            "missing_ppe": missing_ppe,
            "worker_id": worker_id,
            "image_url": image_url,
            "violation_count": violation_count,
            "compliance_rate": compliance_rate,
            "message": AlertTemplates.format_violation_alert(
                TemplateType.MANAGER,
                priority,
                zone,
                camera_id,
                missing_ppe,
                timestamp,
                worker_id,
                image_url,
                violation_count,
                compliance_rate
            )
        }
