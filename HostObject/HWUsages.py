import json

#
# class Any_Usage:
#     def __init__(self):
#         self.all_num: int = 0
#         self.per_min: int = 0
#         self.summary: list = []
#
#     def __dict__(self):
#         return {
#             "all_num": self.all_num,
#             "per_min": self.per_min,
#             "summary": self.summary,
#         }
#
#     def __str__(self):
#         return json.dumps({self.__dict__()})
#
#
# class CPU_Usage(Any_Usage):
#     def __init__(self):
#         super().__init__()
#         self.details: list = []
#
#     def __dict__(self):
#         return {
#             "all_num": self.all_num,
#             "per_min": self.per_min,
#             "summary": self.summary,
#             "details": self.details,
#         }
#
#
# class MEM_Usage(Any_Usage):
#     def __init__(self):
#         super().__init__()
#
#
# class HDD_Usage(Any_Usage):
#     def __init__(self):
#         super().__init__()
#
#
# class GPU_Usage(Any_Usage):
#     def __init__(self):
#         super().__init__()
#         self.details: dict = {}
#
#     def __dict__(self):
#         return {
#             "all_num": self.all_num,
#             "per_min": self.per_min,
#             "summary": self.summary,
#             "details": self.details,
#         }
#
#
# class NET_Usage(Any_Usage):
#     def __init__(self):
#         super().__init__()
#
#
# class FLU_Usage(Any_Usage):
#     def __init__(self):
#         super().__init__()
#
#
# class NAT_Usage(Any_Usage):
#     def __init__(self):
#         super().__init__()
#
#
# class WEB_Usage(Any_Usage):
#     def __init__(self):
#         super().__init__()
#
#
# class PWR_Usage(Any_Usage):
#     def __init__(self):
#         super().__init__()
#         self.cpu_tmp: list = []
#         self.cpu_pwr: list = []
#
#     def __dict__(self):
#         return {
#             "all_num": self.all_num,
#             "per_min": self.per_min,
#             "summary": self.summary,
#             "cpu_tmp": self.cpu_tmp,
#             "cpu_pwr": self.cpu_pwr,
#         }
