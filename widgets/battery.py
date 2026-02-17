from fabric import Fabricator

bat_service: Fabricator = Fabricator(
		interval=100,
		poll_from="acpi -b"
		)
