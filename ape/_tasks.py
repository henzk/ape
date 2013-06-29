"""
APE - a productive environment


"""
FEATURE_SELECTION = []
#Tasks specified here are globally available.
#
#WARNING: importing ape.tasks at the module level leads to a cyclic import
# for global tasks you may want to put here, just import it inside the task function.
# The effect is specific to this file - you may import ape.tasks directly
# at the module level in tasks modules of features.
#

def help(task):
    '''print help on specific task'''
    from ape import tasks
    tasks.help(taskname=task)
