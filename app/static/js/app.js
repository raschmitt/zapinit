const COUNTRIES = [
    { code: 'AF', dial: '+93',  flag: '🇦🇫', name: 'Afghanistan' },
    { code: 'AL', dial: '+355', flag: '🇦🇱', name: 'Albania' },
    { code: 'DZ', dial: '+213', flag: '🇩🇿', name: 'Algeria' },
    { code: 'AR', dial: '+54',  flag: '🇦🇷', name: 'Argentina' },
    { code: 'AU', dial: '+61',  flag: '🇦🇺', name: 'Australia' },
    { code: 'AT', dial: '+43',  flag: '🇦🇹', name: 'Austria' },
    { code: 'AZ', dial: '+994', flag: '🇦🇿', name: 'Azerbaijan' },
    { code: 'BD', dial: '+880', flag: '🇧🇩', name: 'Bangladesh' },
    { code: 'BE', dial: '+32',  flag: '🇧🇪', name: 'Belgium' },
    { code: 'BO', dial: '+591', flag: '🇧🇴', name: 'Bolivia' },
    { code: 'BR', dial: '+55',  flag: '🇧🇷', name: 'Brazil' },
    { code: 'CA', dial: '+1',   flag: '🇨🇦', name: 'Canada' },
    { code: 'CL', dial: '+56',  flag: '🇨🇱', name: 'Chile' },
    { code: 'CN', dial: '+86',  flag: '🇨🇳', name: 'China' },
    { code: 'CO', dial: '+57',  flag: '🇨🇴', name: 'Colombia' },
    { code: 'CR', dial: '+506', flag: '🇨🇷', name: 'Costa Rica' },
    { code: 'HR', dial: '+385', flag: '🇭🇷', name: 'Croatia' },
    { code: 'CZ', dial: '+420', flag: '🇨🇿', name: 'Czech Republic' },
    { code: 'DK', dial: '+45',  flag: '🇩🇰', name: 'Denmark' },
    { code: 'DO', dial: '+1',   flag: '🇩🇴', name: 'Dominican Republic' },
    { code: 'EC', dial: '+593', flag: '🇪🇨', name: 'Ecuador' },
    { code: 'EG', dial: '+20',  flag: '🇪🇬', name: 'Egypt' },
    { code: 'SV', dial: '+503', flag: '🇸🇻', name: 'El Salvador' },
    { code: 'FI', dial: '+358', flag: '🇫🇮', name: 'Finland' },
    { code: 'FR', dial: '+33',  flag: '🇫🇷', name: 'France' },
    { code: 'DE', dial: '+49',  flag: '🇩🇪', name: 'Germany' },
    { code: 'GH', dial: '+233', flag: '🇬🇭', name: 'Ghana' },
    { code: 'GR', dial: '+30',  flag: '🇬🇷', name: 'Greece' },
    { code: 'GT', dial: '+502', flag: '🇬🇹', name: 'Guatemala' },
    { code: 'HN', dial: '+504', flag: '🇭🇳', name: 'Honduras' },
    { code: 'HK', dial: '+852', flag: '🇭🇰', name: 'Hong Kong' },
    { code: 'HU', dial: '+36',  flag: '🇭🇺', name: 'Hungary' },
    { code: 'IN', dial: '+91',  flag: '🇮🇳', name: 'India' },
    { code: 'ID', dial: '+62',  flag: '🇮🇩', name: 'Indonesia' },
    { code: 'IR', dial: '+98',  flag: '🇮🇷', name: 'Iran' },
    { code: 'IE', dial: '+353', flag: '🇮🇪', name: 'Ireland' },
    { code: 'IL', dial: '+972', flag: '🇮🇱', name: 'Israel' },
    { code: 'IT', dial: '+39',  flag: '🇮🇹', name: 'Italy' },
    { code: 'JP', dial: '+81',  flag: '🇯🇵', name: 'Japan' },
    { code: 'KE', dial: '+254', flag: '🇰🇪', name: 'Kenya' },
    { code: 'KR', dial: '+82',  flag: '🇰🇷', name: 'South Korea' },
    { code: 'KW', dial: '+965', flag: '🇰🇼', name: 'Kuwait' },
    { code: 'MY', dial: '+60',  flag: '🇲🇾', name: 'Malaysia' },
    { code: 'MX', dial: '+52',  flag: '🇲🇽', name: 'Mexico' },
    { code: 'MA', dial: '+212', flag: '🇲🇦', name: 'Morocco' },
    { code: 'NL', dial: '+31',  flag: '🇳🇱', name: 'Netherlands' },
    { code: 'NZ', dial: '+64',  flag: '🇳🇿', name: 'New Zealand' },
    { code: 'NG', dial: '+234', flag: '🇳🇬', name: 'Nigeria' },
    { code: 'NO', dial: '+47',  flag: '🇳🇴', name: 'Norway' },
    { code: 'PK', dial: '+92',  flag: '🇵🇰', name: 'Pakistan' },
    { code: 'PA', dial: '+507', flag: '🇵🇦', name: 'Panama' },
    { code: 'PY', dial: '+595', flag: '🇵🇾', name: 'Paraguay' },
    { code: 'PE', dial: '+51',  flag: '🇵🇪', name: 'Peru' },
    { code: 'PH', dial: '+63',  flag: '🇵🇭', name: 'Philippines' },
    { code: 'PL', dial: '+48',  flag: '🇵🇱', name: 'Poland' },
    { code: 'PT', dial: '+351', flag: '🇵🇹', name: 'Portugal' },
    { code: 'QA', dial: '+974', flag: '🇶🇦', name: 'Qatar' },
    { code: 'RO', dial: '+40',  flag: '🇷🇴', name: 'Romania' },
    { code: 'RU', dial: '+7',   flag: '🇷🇺', name: 'Russia' },
    { code: 'SA', dial: '+966', flag: '🇸🇦', name: 'Saudi Arabia' },
    { code: 'SG', dial: '+65',  flag: '🇸🇬', name: 'Singapore' },
    { code: 'ZA', dial: '+27',  flag: '🇿🇦', name: 'South Africa' },
    { code: 'ES', dial: '+34',  flag: '🇪🇸', name: 'Spain' },
    { code: 'SE', dial: '+46',  flag: '🇸🇪', name: 'Sweden' },
    { code: 'CH', dial: '+41',  flag: '🇨🇭', name: 'Switzerland' },
    { code: 'TW', dial: '+886', flag: '🇹🇼', name: 'Taiwan' },
    { code: 'TH', dial: '+66',  flag: '🇹🇭', name: 'Thailand' },
    { code: 'TR', dial: '+90',  flag: '🇹🇷', name: 'Turkey' },
    { code: 'UA', dial: '+380', flag: '🇺🇦', name: 'Ukraine' },
    { code: 'AE', dial: '+971', flag: '🇦🇪', name: 'United Arab Emirates' },
    { code: 'GB', dial: '+44',  flag: '🇬🇧', name: 'United Kingdom' },
    { code: 'US', dial: '+1',   flag: '🇺🇸', name: 'United States' },
    { code: 'UY', dial: '+598', flag: '🇺🇾', name: 'Uruguay' },
    { code: 'VE', dial: '+58',  flag: '🇻🇪', name: 'Venezuela' },
    { code: 'VN', dial: '+84',  flag: '🇻🇳', name: 'Vietnam' },
];

document.addEventListener('DOMContentLoaded', () => {
    const select = document.getElementById('country');
    
    // Always default to Brazil (BR)
    const defaultCountry = 'BR';

    // Sort all countries by dial number ascending
    const sortedCountries = [...COUNTRIES].sort((a, b) => {
        const dialA = parseInt(a.dial.replace('+', ''));
        const dialB = parseInt(b.dial.replace('+', ''));
        return dialA - dialB;
    });

    sortedCountries.forEach(c => {
        const opt = document.createElement('option');
        opt.value = c.dial;
        opt.dataset.code = c.code;
        opt.textContent = `${c.flag} ${c.dial}`;
        opt.title = c.name;
        if (c.code === defaultCountry) opt.selected = true;
        select.appendChild(opt);
    });
});
