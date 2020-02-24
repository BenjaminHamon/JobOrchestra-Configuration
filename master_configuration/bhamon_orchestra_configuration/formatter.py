def platform_to_display_name(platform_identifier):
	if platform_identifier == "android":
		return "Android"
	if platform_identifier == "linux":
		return "Linux"
	if platform_identifier == "windows":
		return "Windows"
	raise ValueError("Unsuppported platform identifier '%s'" % platform_identifier)
